"""
Controlled staging for SMD visible sequences into EASY intermediate files.
"""

import argparse
import json
from pathlib import Path

from src.datasets.class_mapping import get_class_to_id, map_original_class
from src.datasets.smd_mat import discover_smd_sequence_pairs, load_smd_object_frames


def _lazy_import_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("cv2 is required for SMD frame extraction") from exc
    return cv2


def _ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_intermediate_record(sequence_info, frame_index, image_path, width, height, objects):
    class_to_id = get_class_to_id()
    intermediate_objects = []
    for obj in objects:
        easy_class = map_original_class("smd", obj["normalized_class"])
        intermediate_objects.append(
            {
                "original_class": obj["original_class"],
                "easy_class": easy_class,
                "class_id": class_to_id.get(easy_class) if easy_class is not None else None,
                "is_mapped": easy_class is not None,
                "bbox_xyxy": obj["bbox_xyxy"],
                "bbox_xywh": obj["bbox_xywh"],
                "attributes": obj["attributes"],
            }
        )

    return {
        "dataset_key": "smd",
        "dataset_name": "Singapore Maritime Dataset",
        "image_id": image_path.stem,
        "image_path": str(image_path),
        "image_filename": image_path.name,
        "width": int(width),
        "height": int(height),
        "modality": "rgb",
        "split": None,
        "source_annotation_path": str(sequence_info["object_gt_path"]),
        "objects": intermediate_objects,
        "notes": [
            "source_view={}".format(sequence_info["view_name"]),
            "source_sequence_stem={}".format(sequence_info["sequence_stem"]),
            "source_frame_index_zero_based={}".format(frame_index),
            "source_video_path={}".format(sequence_info["video_path"]),
        ],
        "source_sequence_id": sequence_info["sequence_stem"],
        "source_frame_index": frame_index,
        "source_view": sequence_info["view_name"],
    }


def stage_sequence(sequence_info, images_dir, annotations_dir, dry_run=False, overwrite=False):
    cv2 = _lazy_import_cv2()
    frames = load_smd_object_frames(sequence_info["object_gt_path"])
    target_frames = [frame for frame in frames if frame["objects"]]
    view_slug = sequence_info["view_name"].lower()
    sequence_slug = sequence_info["sequence_stem"]

    image_seq_dir = images_dir / view_slug / sequence_slug
    annotation_seq_dir = annotations_dir / view_slug / sequence_slug
    _ensure_dir(image_seq_dir)
    _ensure_dir(annotation_seq_dir)

    summary = {
        "sequence_stem": sequence_slug,
        "view_name": sequence_info["view_name"],
        "source_video_path": str(sequence_info["video_path"]),
        "source_annotation_path": str(sequence_info["object_gt_path"]),
        "frame_count_in_mat": len(frames),
        "annotated_frame_count": len(target_frames),
        "annotated_frame_count_valid_video_range": len(target_frames),
        "written_images": 0,
        "written_annotations": 0,
        "skipped_existing": 0,
        "skipped_out_of_range_frames": 0,
    }

    if dry_run or not target_frames:
        return summary

    cap = cv2.VideoCapture(str(sequence_info["video_path"]))
    if not cap.isOpened():
        raise RuntimeError("Could not open video '{}'".format(sequence_info["video_path"]))

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    valid_target_frames = [frame for frame in target_frames if frame["frame_index"] < video_frame_count]
    summary["video_frame_count"] = video_frame_count
    summary["annotated_frame_count_valid_video_range"] = len(valid_target_frames)
    summary["skipped_out_of_range_frames"] = len(target_frames) - len(valid_target_frames)

    try:
        for frame in valid_target_frames:
            frame_index = frame["frame_index"]
            image_path = image_seq_dir / "{}_frame_{:06d}.png".format(sequence_slug, frame_index)
            annotation_path = annotation_seq_dir / "{}_frame_{:06d}.json".format(sequence_slug, frame_index)

            if not overwrite and image_path.exists() and annotation_path.exists():
                summary["skipped_existing"] += 1
                continue

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, bgr_frame = cap.read()
            if not ok:
                raise RuntimeError(
                    "Could not read frame {} from '{}'".format(frame_index, sequence_info["video_path"])
                )

            if not cv2.imwrite(str(image_path), bgr_frame):
                raise RuntimeError("Could not write image '{}'".format(image_path))

            record = build_intermediate_record(
                sequence_info=sequence_info,
                frame_index=frame_index,
                image_path=image_path,
                width=frame_width,
                height=frame_height,
                objects=frame["objects"],
            )
            annotation_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

            summary["written_images"] += 1
            summary["written_annotations"] += 1
    finally:
        cap.release()

    return summary


def stage_smd(source_root, images_dir, annotations_dir, sequences=None, view=None, max_sequences=None, dry_run=False, overwrite=False):
    candidates = discover_smd_sequence_pairs(source_root)
    if view and view != "all":
        candidates = [item for item in candidates if item["view_name"].lower() == view.lower()]
    if sequences:
        wanted = set(sequences)
        candidates = [item for item in candidates if item["sequence_stem"] in wanted]
    if max_sequences is not None:
        candidates = candidates[: max_sequences]

    summaries = []
    for sequence_info in candidates:
        summaries.append(
            stage_sequence(
                sequence_info=sequence_info,
                images_dir=images_dir,
                annotations_dir=annotations_dir,
                dry_run=dry_run,
                overwrite=overwrite,
            )
        )

    return {
        "source_root": str(source_root),
        "images_dir": str(images_dir),
        "annotations_dir": str(annotations_dir),
        "dry_run": dry_run,
        "sequence_count": len(summaries),
        "summaries": summaries,
    }


def main():
    parser = argparse.ArgumentParser(description="Controlled SMD staging into EASY intermediate records")
    parser.add_argument("--source-root", default="data/raw/smd/source_downloads")
    parser.add_argument("--images-dir", default="data/raw/smd/images")
    parser.add_argument("--annotations-dir", default="data/raw/smd/annotations")
    parser.add_argument("--view", default="all", choices=["all", "vis_onboard", "vis_onshore"])
    parser.add_argument("--sequence", action="append", default=[])
    parser.add_argument("--max-sequences", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--output-manifest", default=None)
    args = parser.parse_args()

    view_map = {
        "all": "all",
        "vis_onboard": "VIS_Onboard",
        "vis_onshore": "VIS_Onshore",
    }

    report = stage_smd(
        source_root=Path(args.source_root),
        images_dir=Path(args.images_dir),
        annotations_dir=Path(args.annotations_dir),
        sequences=args.sequence,
        view=view_map[args.view],
        max_sequences=args.max_sequences,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )

    payload = json.dumps(report, indent=2)
    if args.output_manifest:
        output_path = Path(args.output_manifest)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
        print(str(output_path))
        return

    print(payload)


if __name__ == "__main__":
    main()
