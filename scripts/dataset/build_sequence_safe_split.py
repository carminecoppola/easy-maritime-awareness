#!/usr/bin/env python3
# EASY Maritime Awareness - model repository
# Copyright (c) 2026 Carmine Coppola and EASY contributors.
# SPDX-License-Identifier: BSD-3-Clause
"""Build a sequence-safe train/val/test split of a YOLO detection dataset.

A *sequence* is a video, a recording session or a block of consecutive frames.
Consecutive frames are nearly identical, so splitting a dataset image by image
puts almost the same picture in both the training and the test set and inflates
every metric. This script always assigns a whole sequence to exactly one split
and runs a mandatory leakage audit at the end of every build. See
``outputs/reports/easy_v3_results.md`` for the leakage found in the official
EASY-v1 split.

How sequences are found:

* If the source folder contains a ``manifest.csv`` (columns ``stem`` or
  ``filename``, and ``sequence_id``), it is the source of truth.
* Otherwise the sequence is inferred from the file name:
  ``smd__<video>_frame_<n>`` -> one sequence per source video,
  ``aboships__<YYYYMMDD>_...`` -> one sequence per recording day,
  ``seaships__<prefix><n>`` -> blocks of ``--seaships-block-size`` frames.
* Images with identical content are merged into one sequence (union-find), so an
  accidental duplicate across two sequences cannot end up in two splits.

Assignment is greedy and deterministic for a given seed. Sequences that contain
buoys (the scarce class) are placed first, balancing both image and buoy counts;
the remaining sequences only balance image counts.

Usage:
    python scripts/dataset/build_sequence_safe_split.py \\
        --source-root data/external_sources/aboships_curated \\
        --output-root data/processed/<candidate-name> \\
        --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 --seed 42

The result is a *candidate* to evaluate; it never replaces the frozen
EASY-v1-rgb3-buoy-rebalanced dataset.
"""

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

SPLITS = ("train", "val", "test")
CLASS_NAMES = {0: "boat", 1: "ship", 2: "buoy"}
BUOY_CLASS_ID = 2
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# How much a missing buoy image weighs against a missing image when placing a
# buoy-containing sequence (buoys are rare, so they dominate the decision).
BUOY_WEIGHT = 3.0


@dataclass(frozen=True)
class Item:
    """One image with its labels and the sequence it belongs to."""

    image_path: Path
    label_path: Path
    stem: str
    dataset_prefix: str
    sequence_id: str
    image_fingerprint: str
    objects: tuple


class UnionFind:
    """Merges pseudo-sequences when two images have identical content.

    An accidental duplicate between two different sequences must not be able to
    end up in different splits, so such sequences become one component.
    """

    def __init__(self):
        self.parent = {}

    def add(self, value):
        """Register a value as its own component."""
        self.parent.setdefault(value, value)

    def find(self, value):
        """Return the representative of the component containing ``value``."""
        self.add(value)
        if self.parent[value] != value:
            self.parent[value] = self.find(self.parent[value])
        return self.parent[value]

    def union(self, left, right):
        """Merge the components of ``left`` and ``right``."""
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def parse_args():
    """Parse the command line."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-root", required=True, action="append",
                   help="Dataset to include in the split: either with images/{train,val,test} and "
                        "labels/{train,val,test} (already split elsewhere; it is re-split from scratch), "
                        "or with flat images/ and labels/ folders (a single pool, e.g. an external dataset "
                        "curated on purpose). Repeat the option to merge several sources into one "
                        "sequence-safe split (e.g. the current EASY data plus an additional public dataset). "
                        "Each source keeps its own dataset prefix (from the file name, e.g. 'aboships__...') "
                        "so sequences never collide across sources.")
    p.add_argument("--output-root", required=True)
    p.add_argument("--report", default=None, help="default: <output-root>/split_report.md")
    p.add_argument("--pinned-assignments", default=None,
                   help="Optional YAML {sequence_id: split} to pin some known sequences by hand "
                        "(e.g. stress tests); every other sequence is stratified automatically")
    p.add_argument("--train-ratio", type=float, default=0.7)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--test-ratio", type=float, default=0.15)
    p.add_argument("--seaships-block-size", type=int, default=256,
                   help="SeaShips has no sequence id: this many consecutive frames form one sequence")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def partial_file_fingerprint(path, chunk_size=8192):
    """Cheap content fingerprint: size plus the first and last ``chunk_size`` bytes."""
    stat = path.stat()
    digest = hashlib.sha256()
    digest.update(str(stat.st_size).encode("ascii"))
    with path.open("rb") as handle:
        digest.update(handle.read(chunk_size))
        if stat.st_size > chunk_size:
            handle.seek(max(0, stat.st_size - chunk_size))
            digest.update(handle.read(chunk_size))
    return f"{stat.st_size}:{digest.hexdigest()}"


def parse_label(path):
    """Read a YOLO label file as ``(class, cx, cy, w, h)`` tuples (empty if missing)."""
    if not path.exists():
        return tuple()
    objects = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split()
        if len(parts) != 5:
            continue
        objects.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
    return tuple(objects)


def parse_sequence_id(stem, seaships_block_size):
    """Derive ``(dataset_prefix, source_id, sequence_id)`` from a file stem.

    SMD: one sequence per source video. SeaShips: a block of N consecutive frames,
    because SeaShips does not expose a sequence id in the file name. ABOships: during
    curation the stem is built as ``aboships__<YYYYMMDD>_<original name>``, where the
    date is the original recording-session folder, the only grouping available for
    that dataset: one session/day is one sequence, never a single image.
    """
    if "__" in stem:
        dataset_prefix, source_id = stem.split("__", 1)
    else:
        match = re.match(r"(?P<prefix>[A-Za-z]+)", stem)
        dataset_prefix = match.group("prefix").lower() if match else "unknown"
        source_id = stem

    smd_match = re.match(r"(?P<video>.+?)_frame_(?P<number>\d+)$", source_id)
    if dataset_prefix == "smd" and smd_match:
        return dataset_prefix, source_id, f"smd:{smd_match.group('video')}"

    aboships_match = re.match(r"(?P<date>\d{8})_", source_id)
    if dataset_prefix == "aboships" and aboships_match:
        return dataset_prefix, source_id, f"aboships:{aboships_match.group('date')}"

    generic_match = re.match(r"(?P<prefix>.*?)(?P<number>\d+)$", source_id)
    if dataset_prefix == "seaships" and generic_match:
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        number = int(generic_match.group("number"))
        if raw_prefix:
            return dataset_prefix, source_id, f"seaships:{raw_prefix}"
        return dataset_prefix, source_id, f"seaships:block_{number // seaships_block_size:04d}"

    if generic_match and generic_match.group("prefix").rstrip("_-"):
        raw_prefix = generic_match.group("prefix").rstrip("_-")
        return dataset_prefix, source_id, f"{dataset_prefix}:{raw_prefix}"

    return dataset_prefix, source_id, f"single:{stem}"


def load_manifest(source_root):
    """Load ``manifest.csv`` (columns ``stem``/``filename`` and ``sequence_id``) if present.

    Returns ``{stem: sequence_id}``, or ``{}`` when the file does not exist.
    """
    manifest_path = source_root / "manifest.csv"
    if not manifest_path.exists():
        return {}
    mapping = {}
    with open(manifest_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        stem_field = "stem" if "stem" in (reader.fieldnames or []) else "filename"
        for row in reader:
            stem = Path(row[stem_field]).stem
            mapping[stem] = row["sequence_id"]
    return mapping


def _collect_from_dir(image_dir, label_dir, seaships_block_size, manifest, dataset_tag):
    """Collect the images of one folder as ``Item`` objects."""
    items = []
    if not image_dir.exists():
        return items
    for image_path in sorted(image_dir.iterdir()):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        label_path = label_dir / f"{image_path.stem}.txt"
        if image_path.stem in manifest:
            # An explicit manifest is the source of truth: no regex inference.
            dataset_prefix = dataset_tag
            sequence_id = manifest[image_path.stem]
        else:
            dataset_prefix, _source_id, sequence_id = parse_sequence_id(image_path.stem, seaships_block_size)
        items.append(Item(
            image_path=image_path,
            label_path=label_path,
            stem=image_path.stem,
            dataset_prefix=dataset_prefix,
            sequence_id=sequence_id,
            image_fingerprint=partial_file_fingerprint(image_path),
            objects=parse_label(label_path),
        ))
    return items


def collect_items(source_roots, seaships_block_size):
    """Collect every image of one or more source folders.

    A source is either already split (``images/{train,val,test}``) or a flat pool
    (``images/`` plus ``labels/``). A ``manifest.csv``, when present, takes
    precedence over the sequence inferred from the file name.
    """
    items = []
    for source_root in source_roots:
        manifest = load_manifest(source_root)
        dataset_tag = source_root.name
        found_split_layout = any((source_root / "images" / split).exists() for split in SPLITS)
        if found_split_layout:
            for split in SPLITS:
                items.extend(_collect_from_dir(
                    source_root / "images" / split, source_root / "labels" / split,
                    seaships_block_size, manifest, dataset_tag,
                ))
        else:
            items.extend(_collect_from_dir(
                source_root / "images", source_root / "labels",
                seaships_block_size, manifest, dataset_tag,
            ))
    return items


def merge_duplicate_sequences(items):
    """Group items into components, merging sequences that share an identical image.

    Returns ``{component_id: [items]}``. Without the merge, an accidental duplicate
    could land in two different splits.
    """
    uf = UnionFind()
    by_sequence = defaultdict(list)
    by_fingerprint = defaultdict(list)
    for item in items:
        uf.add(item.sequence_id)
        by_sequence[item.sequence_id].append(item)
        by_fingerprint[item.image_fingerprint].append(item)
    for group in by_fingerprint.values():
        if len(group) <= 1:
            continue
        anchor = group[0].sequence_id
        for item in group[1:]:
            uf.union(anchor, item.sequence_id)
    components = defaultdict(list)
    for sequence_id, seq_items in by_sequence.items():
        components[uf.find(sequence_id)].extend(seq_items)
    return dict(components)


def sequence_stats(component_id, items):
    """Image, per-class object and buoy-image counts of one component."""
    class_counts = Counter({cid: 0 for cid in CLASS_NAMES})
    for item in items:
        for class_id, *_ in item.objects:
            class_counts[class_id] += 1
    return {
        "component_id": component_id,
        "images": len(items),
        "class_counts": dict(class_counts),
        "buoy_images": sum(1 for item in items if any(c == BUOY_CLASS_ID for c, *_ in item.objects)),
    }


def stratified_assign(components_stats, pinned, train_ratio, val_ratio, test_ratio, seed):
    """Assign every sequence (never a single image) to exactly one split.

    Pinned sequences go where requested. The others are shuffled deterministically
    (seed) and assigned greedily to the split that needs them most to stay close to
    the targets for images AND for buoys, so stratification on buoys happens at
    sequence level instead of image level (the bug behind the leakage in the
    official EASY-v1 split).
    """
    targets = {"train": train_ratio, "val": val_ratio, "test": test_ratio}
    total = sum(t for t in targets.values())
    targets = {k: v / total for k, v in targets.items()}

    assignment = {}
    running_images = {s: 0 for s in SPLITS}
    running_buoy_images = {s: 0 for s in SPLITS}

    remaining = []
    for component_id, stats in components_stats.items():
        if component_id in pinned:
            split = pinned[component_id]
            assignment[component_id] = split
            running_images[split] += stats["images"]
            running_buoy_images[split] += stats["buoy_images"]
        else:
            remaining.append(stats)

    rng = random.Random(seed)
    # Seeded shuffle so that, at equal buoy counts, no source dataset is
    # systematically favoured.
    rng.shuffle(remaining)
    buoy_sequences = [s for s in remaining if s["buoy_images"] > 0]
    plain_sequences = [s for s in remaining if s["buoy_images"] == 0]
    buoy_sequences.sort(key=lambda s: -s["buoy_images"])

    total_images = sum(s["images"] for s in components_stats.values())
    total_buoy_images = sum(s["buoy_images"] for s in components_stats.values()) or 1

    # Phase 1: place ONLY the sequences with buoys (the scarce resource: there are
    # few in the whole dataset), weighing both the image deficit and the buoy deficit.
    for stats in buoy_sequences:
        best_split, best_score = None, None
        for split in SPLITS:
            image_deficit = (targets[split] * total_images - running_images[split]) / total_images
            buoy_deficit = (targets[split] * total_buoy_images - running_buoy_images[split]) / total_buoy_images
            score = image_deficit + BUOY_WEIGHT * buoy_deficit
            if best_score is None or score > best_score:
                best_score, best_split = score, split
        assignment[stats["component_id"]] = best_split
        running_images[best_split] += stats["images"]
        running_buoy_images[best_split] += stats["buoy_images"]

    # Phase 2: the rest (no buoys involved) only balances image counts. It is kept
    # separate on purpose: a buoy deficit that can no longer be filled (the buoys
    # are used up) must not keep distorting the distribution of the remaining images.
    for stats in plain_sequences:
        best_split, best_score = None, None
        for split in SPLITS:
            image_deficit = targets[split] * total_images - running_images[split]
            if best_score is None or image_deficit > best_score:
                best_score, best_split = image_deficit, split
        assignment[stats["component_id"]] = best_split
        running_images[best_split] += stats["images"]

    return assignment


def reset_output(output_root, overwrite):
    """Create an empty output tree; refuse to touch an existing one without ``--overwrite``."""
    if output_root.exists():
        if not overwrite:
            raise FileExistsError(f"{output_root} already exists; pass --overwrite to rebuild it")
        shutil.rmtree(output_root)
    for split in SPLITS:
        (output_root / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_root / "labels" / split).mkdir(parents=True, exist_ok=True)


def link_or_copy(source, target):
    """Hard-link ``source`` to ``target`` (no extra disk space), copying when linking fails."""
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def write_dataset(items_by_split, output_root):
    """Materialise the split on disk and write the Ultralytics ``dataset.yaml``."""
    for split, items in items_by_split.items():
        for item in items:
            link_or_copy(item.image_path, output_root / "images" / split / item.image_path.name)
            if item.label_path.exists():
                link_or_copy(item.label_path, output_root / "labels" / split / item.label_path.name)
    dataset_yaml = {
        "path": str(output_root.resolve()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 3,
        "names": CLASS_NAMES,
    }
    (output_root / "dataset.yaml").write_text(
        yaml.safe_dump(dataset_yaml, sort_keys=False, default_flow_style=False), encoding="utf-8",
    )


def audit_no_cross_split_leakage(assignment, components):
    """Return ``{sequence_id: splits}`` for every sequence that appears in more than one split.

    An empty result is the pass condition of the audit.
    """
    sequence_to_split = defaultdict(set)
    for component_id, items in components.items():
        split = assignment[component_id]
        for item in items:
            sequence_to_split[item.sequence_id].add(split)
    violations = {seq: splits for seq, splits in sequence_to_split.items() if len(splits) > 1}
    return violations


def table(headers, rows):
    """Render a Markdown table."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(output_root, source_roots, items_by_split, components_by_split, assignment, violations, args):
    """Build the Markdown report: audit verdict, counts per split, class mix and buoy sequences."""
    split_rows = []
    class_rows = []
    for split in SPLITS:
        items = items_by_split[split]
        class_counts = Counter({cid: 0 for cid in CLASS_NAMES})
        for item in items:
            for class_id, *_ in item.objects:
                class_counts[class_id] += 1
        n_sequences = len(components_by_split[split])
        split_rows.append([split, len(items), sum(class_counts.values()), n_sequences])
        total = sum(class_counts.values())
        for class_id, name in CLASS_NAMES.items():
            count = class_counts[class_id]
            pct = "0.00%" if total == 0 else f"{count / total * 100:.2f}%"
            class_rows.append([split, name, count, pct])

    buoy_seq_rows = []
    for split in SPLITS:
        for stats in sorted(components_by_split[split], key=lambda s: -s["buoy_images"]):
            if stats["buoy_images"] > 0:
                buoy_seq_rows.append([split, stats["component_id"], stats["images"], stats["buoy_images"]])

    audit_status = "PASS: no sequence is split across sets" if not violations else "FAIL"
    lines = [
        "# Sequence-safe split report",
        "",
        f"- Sources: {', '.join(f'`{p}`' for p in source_roots)}",
        f"- Output: `{output_root}`",
        f"- Target ratios: train={args.train_ratio}, val={args.val_ratio}, test={args.test_ratio}",
        f"- Seed: {args.seed}",
        "",
        "## Leakage audit (mandatory)",
        "",
        f"**{audit_status}**",
        "",
    ]
    if violations:
        lines.append("Split sequences (BUG: this must never happen by construction):")
        for seq, splits in violations.items():
            lines.append(f"- `{seq}`: {sorted(splits)}")
        lines.append("")

    lines += [
        "## Counts per split",
        "",
        table(["Split", "Images", "Objects", "Sequences"], split_rows),
        "",
        "## Class distribution",
        "",
        table(["Split", "Class", "Objects", "%"], class_rows),
        "",
        "## Buoy distribution per sequence (caution: scarce data)",
        "",
        "The current dataset has few sequences with buoys. A correct, sequence-level "
        "stratification (as applied here) can still produce a split with zero or very "
        "few buoys in a given set, simply because there are not enough buoy sequences "
        "to distribute evenly. This is NOT a bug of the script: it is the data-scarcity "
        "problem already observed in the EASY-v2/v2.1 attempts (buoy recall collapsed "
        "to 0.00). Check this table before training.",
        "",
        table(["Split", "Sequence", "Images", "Images with buoys"], buoy_seq_rows) if buoy_seq_rows else "_No sequence with buoys found._",
        "",
    ]
    return "\n".join(lines) + "\n"


def main():
    """Collect, assign, audit and write the split."""
    args = parse_args()
    source_roots = [Path(p) for p in args.source_root]
    output_root = Path(args.output_root)
    report_path = Path(args.report) if args.report else output_root / "split_report.md"

    pinned = {}
    if args.pinned_assignments:
        with open(args.pinned_assignments) as fh:
            pinned = yaml.safe_load(fh) or {}

    items = collect_items(source_roots, args.seaships_block_size)
    if not items:
        raise SystemExit(f"No image found under {source_roots}")

    components = merge_duplicate_sequences(items)
    components_stats = {cid: sequence_stats(cid, its) for cid, its in components.items()}

    unknown_pinned = sorted(set(pinned) - set(components_stats))
    if unknown_pinned:
        raise SystemExit(f"Pinned sequences not found in the dataset: {unknown_pinned}")

    assignment = stratified_assign(
        components_stats, pinned, args.train_ratio, args.val_ratio, args.test_ratio, args.seed,
    )

    violations = audit_no_cross_split_leakage(assignment, components)
    if violations:
        raise RuntimeError(f"Structural leakage detected (this should be impossible): {violations}")

    items_by_split = {s: [] for s in SPLITS}
    components_by_split = {s: [] for s in SPLITS}
    for component_id, comp_items in components.items():
        split = assignment[component_id]
        items_by_split[split].extend(comp_items)
        components_by_split[split].append(components_stats[component_id])

    reset_output(output_root, args.overwrite)
    write_dataset(items_by_split, output_root)

    report = render_report(output_root, source_roots, items_by_split, components_by_split, assignment, violations, args)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    build_summary = {
        "source_roots": [str(p) for p in source_roots],
        "output_root": str(output_root),
        "seed": args.seed,
        "ratios": {"train": args.train_ratio, "val": args.val_ratio, "test": args.test_ratio},
        "pinned_assignments": pinned,
        "assignment": assignment,
        "leakage_audit": "PASS" if not violations else "FAIL",
        "counts": {s: len(items_by_split[s]) for s in SPLITS},
    }
    (output_root / "build_summary.json").write_text(json.dumps(build_summary, indent=2), encoding="utf-8")

    print(f"Leakage audit: {'PASS' if not violations else 'FAIL'}")
    for s in SPLITS:
        print(f"{s}: {len(items_by_split[s])} images, {len(components_by_split[s])} sequences")
    print(f"Report: {report_path}")
    print(f"Dataset: {output_root}")


if __name__ == "__main__":
    main()
