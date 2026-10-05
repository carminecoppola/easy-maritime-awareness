# EASY Maritime Awareness - model repository
# Copyright (c) 2026 Carmine Coppola and EASY contributors.
# SPDX-License-Identifier: BSD-3-Clause
"""Tests for the sequence-safe split builder.

They protect the property the whole repository rests on: no sequence (video,
recording day or block of frames) is ever spread across train, val and test.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("split_builder", ROOT / "scripts/dataset/build_sequence_safe_split.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def make_item(stem, fingerprint, objects=()):
    """Build an Item whose sequence id is inferred from ``stem``."""
    prefix, _source, sequence = builder.parse_sequence_id(stem, seaships_block_size=256)
    return builder.Item(
        image_path=Path(f"{stem}.jpg"), label_path=Path(f"{stem}.txt"), stem=stem,
        dataset_prefix=prefix, sequence_id=sequence, image_fingerprint=fingerprint, objects=tuple(objects),
    )


class SequenceIdTests(unittest.TestCase):
    def test_smd_frames_of_one_video_share_a_sequence(self):
        a = builder.parse_sequence_id("smd__MVI_1469_VIS_frame_001", 256)
        b = builder.parse_sequence_id("smd__MVI_1469_VIS_frame_900", 256)
        self.assertEqual(a[2], b[2])
        self.assertEqual(a[2], "smd:MVI_1469_VIS")

    def test_aboships_sequence_is_the_recording_day(self):
        self.assertEqual(builder.parse_sequence_id("aboships__20180626_img_17", 256)[2], "aboships:20180626")

    def test_seaships_frames_are_grouped_in_blocks(self):
        near = builder.parse_sequence_id("seaships__001253", 256)[2]
        same_block = builder.parse_sequence_id("seaships__001100", 256)[2]
        next_block = builder.parse_sequence_id("seaships__001300", 256)[2]
        self.assertEqual(near, same_block)
        self.assertNotEqual(near, next_block)


class AssignmentTests(unittest.TestCase):
    def build(self, items, seed=42):
        components = builder.merge_duplicate_sequences(items)
        stats = {cid: builder.sequence_stats(cid, its) for cid, its in components.items()}
        assignment = builder.stratified_assign(stats, {}, 0.7, 0.15, 0.15, seed)
        return components, assignment

    def test_no_sequence_is_split_across_sets(self):
        items = []
        for video in range(12):
            for frame in range(10):
                buoy = [(2, 0.5, 0.5, 0.1, 0.1)] if video % 4 == 0 else [(0, 0.5, 0.5, 0.1, 0.1)]
                items.append(make_item(f"smd__VID{video}_frame_{frame:03d}", f"fp-{video}-{frame}", buoy))
        components, assignment = self.build(items)
        self.assertEqual(builder.audit_no_cross_split_leakage(assignment, components), {})
        self.assertEqual(set(assignment.values()) <= set(builder.SPLITS), True)

    def test_identical_images_merge_two_sequences(self):
        items = [make_item("smd__A_frame_001", "same"), make_item("smd__B_frame_001", "same"),
                 make_item("smd__C_frame_001", "other")]
        components = builder.merge_duplicate_sequences(items)
        self.assertEqual(len(components), 2)

    def test_assignment_is_deterministic_for_a_seed(self):
        items = [make_item(f"smd__V{v}_frame_{f}", f"{v}-{f}") for v in range(8) for f in range(5)]
        _, first = self.build(items, seed=7)
        _, second = self.build(items, seed=7)
        self.assertEqual(first, second)

    def test_audit_detects_a_split_sequence(self):
        item_a = make_item("smd__V_frame_001", "a")
        item_b = make_item("smd__V_frame_002", "b")
        components = {"x": [item_a], "y": [item_b]}
        violations = builder.audit_no_cross_split_leakage({"x": "train", "y": "test"}, components)
        self.assertEqual(set(violations), {"smd:V"})


class EndToEndTests(unittest.TestCase):
    def test_a_flat_pool_is_split_and_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/images").mkdir(parents=True)
            (root / "src/labels").mkdir(parents=True)
            for video in range(6):
                for frame in range(4):
                    stem = f"smd__V{video}_frame_{frame:03d}"
                    (root / "src/images" / f"{stem}.jpg").write_bytes(f"{video}-{frame}".encode() * 50)
                    (root / "src/labels" / f"{stem}.txt").write_text("0 0.5 0.5 0.2 0.2\n")
            items = builder.collect_items([root / "src"], 256)
            components = builder.merge_duplicate_sequences(items)
            stats = {cid: builder.sequence_stats(cid, its) for cid, its in components.items()}
            assignment = builder.stratified_assign(stats, {}, 0.7, 0.15, 0.15, 1)
            by_split = {s: [] for s in builder.SPLITS}
            for cid, its in components.items():
                by_split[assignment[cid]].extend(its)
            out = root / "out"
            builder.reset_output(out, overwrite=False)
            builder.write_dataset(by_split, out)
            written = sum(len(list((out / "images" / s).glob("*.jpg"))) for s in builder.SPLITS)
            self.assertEqual(written, 24)
            self.assertTrue((out / "dataset.yaml").is_file())
            with self.assertRaises(FileExistsError):
                builder.reset_output(out, overwrite=False)


if __name__ == "__main__":
    unittest.main()
