#!/usr/bin/env python3
# EASY Maritime Awareness - model repository
# Copyright (c) 2026 Carmine Coppola and EASY contributors.
# SPDX-License-Identifier: BSD-3-Clause
"""Evaluate an EASY model on a sample of MODD2, an external benchmark never used in training.

MODD2 (Marine Obstacle Detection Dataset 2, ViCoS, University of Ljubljana) annotates
generic "obstacle" boxes without a class (``annotations_v2_redone/*/ground_truth/*.mat``).
The evaluation is therefore class-agnostic: a detection of ANY EASY class that matches
a MODD2 box by IoU counts as a true positive. The numbers are not comparable with the
per-class mAP of the internal test set.

Usage:
    python scripts/validation/modd2_external_eval.py \
        --video-zip <path to MODD2_video_data_rectified.zip> \
        --sample-plan <path to modd2_sample_plan.json> \
        --weights outputs/experiments/.../best.pt \
        --out-dir data/external_validation/modd2_v1 \
        --report outputs/reports/easy_v1_modd2_external_eval.json

Requires the ``ultralytics`` package (see requirements-training.txt).
"""

import argparse
import json
import os
import zipfile
from datetime import datetime, timezone

from ultralytics import YOLO


def parse_args():
    """Parse the command line."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video-zip", required=True)
    p.add_argument("--sample-plan", required=True)
    p.add_argument("--weights", required=True)
    p.add_argument("--out-dir", required=True, help="where to extract the sampled frames")
    p.add_argument("--report", required=True)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou-match", type=float, default=0.3,
                    help="IoU threshold to count a detection as a match with a MODD2 box")
    return p.parse_args()


def iou_xywh(box_a, box_b):
    """Intersection over union of two (x, y, w, h) boxes."""
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b
    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh
    ix1, iy1 = max(ax, bx), max(ay, by)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def xyxy_to_xywh(x1, y1, x2, y2):
    """Convert corner coordinates to (x, y, w, h)."""
    return (x1, y1, x2 - x1, y2 - y1)


def extract_frames(video_zip_path, plan, out_dir):
    """Extract the planned left-camera frames from the ZIP and record their paths in ``plan``."""
    images_dir = os.path.join(out_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    extracted = {}
    with zipfile.ZipFile(video_zip_path) as zf:
        names = set(zf.namelist())
        for entry in plan:
            seq = entry["sequence"]
            frame_num = entry["frame_num"]
            zpath = f"video_data/{seq}/framesRectified/{frame_num:08d}L.jpg"
            if zpath not in names:
                continue
            out_name = f"{seq}__{frame_num:08d}L.jpg"
            out_path = os.path.join(images_dir, out_name)
            if not os.path.exists(out_path):
                with zf.open(zpath) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
            extracted[id(entry)] = out_path
            entry["_image_path"] = out_path
    return images_dir


def evaluate(model, plan, conf, iou_match):
    """Run the model on every frame and match detections to ground truth.

    Matching is greedy by descending IoU, one detection per ground-truth box. Returns the
    summary (object-level, class-agnostic recall and precision) and the per-image details.
    """
    per_image = []
    total_gt = 0
    total_det = 0
    matched_gt = 0
    matched_det = 0

    for entry in plan:
        img_path = entry.get("_image_path")
        if not img_path:
            continue
        gt_boxes = entry["boxes_xywh"]
        result = model.predict(source=img_path, conf=conf, verbose=False)[0]
        det_boxes = []
        for box in result.boxes:
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            det_boxes.append({
                "xywh": xyxy_to_xywh(x1, y1, x2, y2),
                "class": model.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
            })

        gt_hit = [False] * len(gt_boxes)
        det_hit = [False] * len(det_boxes)
        # greedy matching by descending IoU
        pairs = []
        for gi, gb in enumerate(gt_boxes):
            for di, db in enumerate(det_boxes):
                iou = iou_xywh(gb, db["xywh"])
                if iou >= iou_match:
                    pairs.append((iou, gi, di))
        pairs.sort(reverse=True)
        for iou, gi, di in pairs:
            if not gt_hit[gi] and not det_hit[di]:
                gt_hit[gi] = True
                det_hit[di] = True

        total_gt += len(gt_boxes)
        total_det += len(det_boxes)
        matched_gt += sum(gt_hit)
        matched_det += sum(det_hit)

        per_image.append({
            "sequence": entry["sequence"],
            "frame": entry["frame_file"],
            "num_gt": len(gt_boxes),
            "num_det": len(det_boxes),
            "num_matched": sum(gt_hit),
            "detections": det_boxes,
        })

    recall = matched_gt / total_gt if total_gt else None
    precision = matched_det / total_det if total_det else None
    return {
        "total_ground_truth_obstacles": total_gt,
        "total_detections": total_det,
        "matched_ground_truth": matched_gt,
        "matched_detections": matched_det,
        "object_level_recall_class_agnostic": round(recall, 4) if recall is not None else None,
        "object_level_precision_class_agnostic": round(precision, 4) if precision is not None else None,
    }, per_image


def main():
    """Extract frames, evaluate the model and write the JSON report."""
    args = parse_args()

    with open(args.sample_plan) as fh:
        plan = json.load(fh)

    print(f"Extracting frames from {args.video_zip} ...")
    extract_frames(args.video_zip, plan, args.out_dir)
    present = [e for e in plan if e.get("_image_path")]
    print(f"Frames extracted: {len(present)} / {len(plan)}")

    print(f"Loading model {args.weights} ...")
    model = YOLO(args.weights)

    print("Running inference and IoU matching ...")
    summary, per_image = evaluate(model, present, args.conf, args.iou_match)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weights": args.weights,
        "dataset": "MODD2 (ViCoS, Univ. of Ljubljana) - class-agnostic sample",
        "conf_threshold": args.conf,
        "iou_match_threshold": args.iou_match,
        "num_frames_evaluated": len(present),
        "note": (
            "Class-agnostic evaluation: MODD2 in this format does not distinguish "
            "boat/ship/buoy, so every EASY detection (of any class) that matches a "
            "MODD2 box by IoU is counted as an object-level true positive. Not "
            "directly comparable with the per-class mAP of the internal test set."
        ),
        "summary": summary,
        "per_image": per_image,
    }

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w") as fh:
        json.dump(report, fh, indent=2)

    print(f"Object-level recall (class-agnostic): {summary['object_level_recall_class_agnostic']}")
    print(f"Object-level precision (class-agnostic): {summary['object_level_precision_class_agnostic']}")
    print(f"GT: {summary['total_ground_truth_obstacles']}  Det: {summary['total_detections']}  Matched: {summary['matched_ground_truth']}")
    print(f"Report written to: {args.report}")


if __name__ == "__main__":
    main()
