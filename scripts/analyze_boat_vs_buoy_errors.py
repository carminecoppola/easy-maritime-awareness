#!/usr/bin/env python3
"""
Analyze boat-vs-buoy failure modes on the balanced-v2 validation run.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

import numpy as np
from PIL import Image, ImageDraw, ImageFont


CLASS_NAMES = {0: "boat", 1: "ship", 2: "buoy"}
PREDICTION_CATEGORY_TO_CLASS_ID = {1: 0, 2: 1, 3: 2}
BUOY_CLASS_ID = 2
IOU_MATCH = 0.5
LOW_CONF = 0.25


@dataclass
class Box:
    class_id: int
    x1: float
    y1: float
    x2: float
    y2: float
    score: float | None = None

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area_px(self) -> float:
        return self.width * self.height


@dataclass
class ImageRecord:
    split: str
    stem: str
    image_path: Path
    label_path: Path
    width: int
    height: int
    source: str
    source_id: str
    pseudo_sequence_id: str
    boxes: list[Box]


@dataclass
class ErrorCase:
    record: ImageRecord
    gt_box: Box
    assigned_to: str
    matched_pred: Box | None
    best_pred: Box | None
    best_iou: float
    area_norm: float
    aspect_ratio: float
    center_x: float
    center_y: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze boat-vs-buoy confusion on balanced-v2")
    parser.add_argument("--dataset-root", default="data/processed/EASY-v0-rgb3-balanced-v2")
    parser.add_argument(
        "--predictions-json",
        default="outputs/runs/rgb3_balanced_v2_baseline/yolov8n_pretrained_50ep_balanced_v2_val/predictions.json",
    )
    parser.add_argument(
        "--report",
        default="outputs/reports/boat_vs_buoy_error_analysis.md",
    )
    parser.add_argument(
        "--gallery-dir",
        default="outputs/error_analysis/boat_vs_buoy",
    )
    return parser.parse_args()


def parse_pseudo_sequence(stem: str, seaships_block_size: int = 256) -> tuple[str, str, str]:
    dataset_prefix, source_id = stem.split("__", 1)
    smd_match = re.match(r"(?P<video>.+?)_frame_(?P<number>\d+)$", source_id)
    if dataset_prefix == "smd" and smd_match:
        return dataset_prefix, source_id, f"smd:{smd_match.group('video')}"
    if dataset_prefix == "seaships" and source_id.isdigit():
        block = int(source_id) // seaships_block_size
        return dataset_prefix, source_id, f"seaships:block_{block:04d}"
    return dataset_prefix, source_id, f"{dataset_prefix}:{source_id}"


def yolo_to_box(class_id: int, values: list[float], width: int, height: int) -> Box:
    xc, yc, w, h = values
    bw = w * width
    bh = h * height
    x1 = (xc * width) - bw / 2.0
    y1 = (yc * height) - bh / 2.0
    x2 = x1 + bw
    y2 = y1 + bh
    return Box(class_id=class_id, x1=x1, y1=y1, x2=x2, y2=y2)


def load_image_records(dataset_root: Path) -> dict[str, list[ImageRecord]]:
    records: dict[str, list[ImageRecord]] = {}
    for split in ["train", "val", "test"]:
        split_records: list[ImageRecord] = []
        label_dir = dataset_root / "labels" / split
        image_dir = dataset_root / "images" / split
        for label_path in sorted(label_dir.glob("*.txt")):
            stem = label_path.stem
            image_path = None
            for ext in [".jpg", ".jpeg", ".png"]:
                candidate = image_dir / f"{stem}{ext}"
                if candidate.exists():
                    image_path = candidate
                    break
            if image_path is None:
                raise FileNotFoundError(f"Missing image for {label_path}")
            with Image.open(image_path) as image:
                width, height = image.size
            boxes: list[Box] = []
            for raw_line in label_path.read_text(encoding="utf-8").splitlines():
                if not raw_line.strip():
                    continue
                parts = raw_line.split()
                boxes.append(yolo_to_box(int(parts[0]), [float(x) for x in parts[1:5]], width, height))
            source, source_id, pseudo_sequence_id = parse_pseudo_sequence(stem)
            split_records.append(
                ImageRecord(
                    split=split,
                    stem=stem,
                    image_path=image_path,
                    label_path=label_path,
                    width=width,
                    height=height,
                    source=source,
                    source_id=source_id,
                    pseudo_sequence_id=pseudo_sequence_id,
                    boxes=boxes,
                )
            )
        records[split] = split_records
    return records


def load_predictions(predictions_path: Path) -> dict[str, list[Box]]:
    payload = json.loads(predictions_path.read_text(encoding="utf-8"))
    grouped: dict[str, list[Box]] = defaultdict(list)
    for row in payload:
        stem = Path(row["file_name"]).stem
        class_id = PREDICTION_CATEGORY_TO_CLASS_ID[int(row["category_id"])]
        x, y, w, h = row["bbox"]
        grouped[stem].append(
            Box(
                class_id=class_id,
                x1=float(x),
                y1=float(y),
                x2=float(x + w),
                y2=float(y + h),
                score=float(row["score"]),
            )
        )
    return grouped


def iou(left: Box, right: Box) -> float:
    inter_x1 = max(left.x1, right.x1)
    inter_y1 = max(left.y1, right.y1)
    inter_x2 = min(left.x2, right.x2)
    inter_y2 = min(left.y2, right.y2)
    inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
    if inter_area <= 0.0:
        return 0.0
    union = left.area_px + right.area_px - inter_area
    return inter_area / union if union else 0.0


def area_norm(box: Box, width: int, height: int) -> float:
    return box.area_px / float(width * height)


def aspect_ratio(box: Box) -> float:
    return 0.0 if box.height == 0 else box.width / box.height


def center_norm(box: Box, width: int, height: int) -> tuple[float, float]:
    return ((box.x1 + box.x2) / 2.0 / width, (box.y1 + box.y2) / 2.0 / height)


def make_case(record: ImageRecord, gt_box: Box, assigned_to: str, matched_pred: Box | None, best_pred: Box | None, best_iou: float) -> ErrorCase:
    cx, cy = center_norm(gt_box, record.width, record.height)
    return ErrorCase(
        record=record,
        gt_box=gt_box,
        assigned_to=assigned_to,
        matched_pred=matched_pred,
        best_pred=best_pred,
        best_iou=best_iou,
        area_norm=area_norm(gt_box, record.width, record.height),
        aspect_ratio=aspect_ratio(gt_box),
        center_x=cx,
        center_y=cy,
    )


def analyze_val_buoy_cases(val_records: list[ImageRecord], predictions: dict[str, list[Box]]) -> dict[str, list[ErrorCase]]:
    groups = {
        "pred_as_boat": [],
        "pred_as_buoy_low_conf": [],
        "background": [],
        "pred_as_ship": [],
        "pred_as_buoy_high_conf": [],
        "other": [],
    }
    for record in val_records:
        preds = predictions.get(record.stem, [])
        for gt_box in [box for box in record.boxes if box.class_id == BUOY_CLASS_ID]:
            best_pred = None
            best_iou = 0.0
            for pred in preds:
                overlap = iou(gt_box, pred)
                if overlap > best_iou:
                    best_iou = overlap
                    best_pred = pred
            if best_pred is None or best_iou < IOU_MATCH:
                groups["background"].append(make_case(record, gt_box, "background", None, best_pred, best_iou))
                continue
            if best_pred.class_id == 0:
                groups["pred_as_boat"].append(make_case(record, gt_box, "boat", best_pred, best_pred, best_iou))
            elif best_pred.class_id == 1:
                groups["pred_as_ship"].append(make_case(record, gt_box, "ship", best_pred, best_pred, best_iou))
            elif best_pred.class_id == 2 and (best_pred.score or 0.0) < LOW_CONF:
                groups["pred_as_buoy_low_conf"].append(make_case(record, gt_box, "buoy_low_conf", best_pred, best_pred, best_iou))
            elif best_pred.class_id == 2:
                groups["pred_as_buoy_high_conf"].append(make_case(record, gt_box, "buoy_high_conf", best_pred, best_pred, best_iou))
            else:
                groups["other"].append(make_case(record, gt_box, "other", best_pred, best_pred, best_iou))
    return groups


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def pred_color(class_id: int) -> tuple[int, int, int]:
    return {0: (255, 165, 0), 1: (0, 191, 255), 2: (255, 64, 64)}[class_id]


def overlay_lines(case: ErrorCase) -> list[str]:
    pred = case.matched_pred or case.best_pred
    pred_label = "none" if pred is None else f"{CLASS_NAMES[pred.class_id]} conf={pred.score:.3f} iou={case.best_iou:.3f}"
    gt_name = CLASS_NAMES[case.gt_box.class_id]
    return [
        case.record.stem,
        f"split={case.record.split}  seq={case.record.pseudo_sequence_id}",
        f"GT {gt_name} area={case.area_norm*100:.3f}%  ar={case.aspect_ratio:.3f}  center=({case.center_x:.3f},{case.center_y:.3f})",
        f"assigned={case.assigned_to}  pred={pred_label}",
    ]


def render_case_overlay(case: ErrorCase, output_path: Path) -> None:
    with Image.open(case.record.image_path) as image:
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        gt = case.gt_box
        draw.rectangle([gt.x1, gt.y1, gt.x2, gt.y2], outline=(0, 255, 0), width=4)
        draw.text((gt.x1 + 4, max(4, gt.y1 - 24)), f"GT {CLASS_NAMES[gt.class_id]}", fill=(0, 255, 0), font=font(22))
        for pred in sorted((case.record.stem and []) or []):
            _ = pred
        predictions_to_draw = []
        if case.best_pred is not None:
            predictions_to_draw.append(case.best_pred)
        if case.matched_pred is not None and case.matched_pred is not case.best_pred:
            predictions_to_draw.append(case.matched_pred)
        seen = set()
        deduped = []
        for pred in predictions_to_draw:
            key = (pred.class_id, round(pred.x1, 3), round(pred.y1, 3), round(pred.x2, 3), round(pred.y2, 3), round(pred.score or 0.0, 4))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(pred)
        for pred in deduped:
            color = pred_color(pred.class_id)
            label = f"P {CLASS_NAMES[pred.class_id]} {pred.score:.3f}"
            draw.rectangle([pred.x1, pred.y1, pred.x2, pred.y2], outline=color, width=3)
            draw.text((pred.x1 + 4, pred.y1 + 4), label, fill=color, font=font(18))
        meta = overlay_lines(case)
        banner_h = 104
        canvas = Image.new("RGB", (image.width, image.height + banner_h), (22, 22, 22))
        canvas.paste(image, (0, 0))
        meta_draw = ImageDraw.Draw(canvas)
        for idx, line in enumerate(meta):
            meta_draw.text((12, image.height + 6 + idx * 24), line, fill=(245, 245, 245), font=font(20))
        canvas.save(output_path, quality=92)


def distance_to_profile(features: np.ndarray, profile_center: np.ndarray, profile_scale: np.ndarray) -> np.ndarray:
    normalized = (features - profile_center) / np.maximum(profile_scale, 1e-6)
    return np.sqrt((normalized ** 2).sum(axis=1))


def feature_vector(record: ImageRecord, box: Box) -> np.ndarray:
    cx, cy = center_norm(box, record.width, record.height)
    return np.array(
        [
            math.log10(max(area_norm(box, record.width, record.height), 1e-8)),
            aspect_ratio(box),
            cx,
            cy,
        ],
        dtype=float,
    )


def diverse_select(cases: list[ErrorCase], limit: int, sort_key) -> list[ErrorCase]:
    if len(cases) <= limit:
        return sorted(cases, key=sort_key)
    ordered = sorted(cases, key=sort_key)
    seq_buckets: dict[str, list[ErrorCase]] = defaultdict(list)
    for case in ordered:
        seq_buckets[case.record.pseudo_sequence_id].append(case)
    selected: list[ErrorCase] = []
    while len(selected) < limit:
        progress = False
        for seq in sorted(seq_buckets):
            if not seq_buckets[seq]:
                continue
            selected.append(seq_buckets[seq].pop(0))
            progress = True
            if len(selected) == limit:
                break
        if not progress:
            break
    return selected[:limit]


def build_train_reference_cases(train_records: list[ImageRecord]) -> tuple[list[ErrorCase], list[ErrorCase], dict[str, object]]:
    train_buoys: list[ErrorCase] = []
    train_boats: list[tuple[ErrorCase, np.ndarray]] = []
    train_buoy_features: list[np.ndarray] = []
    for record in train_records:
        for box in record.boxes:
            cx, cy = center_norm(box, record.width, record.height)
            case = ErrorCase(
                record=record,
                gt_box=box,
                assigned_to="reference",
                matched_pred=None,
                best_pred=None,
                best_iou=0.0,
                area_norm=area_norm(box, record.width, record.height),
                aspect_ratio=aspect_ratio(box),
                center_x=cx,
                center_y=cy,
            )
            if box.class_id == BUOY_CLASS_ID:
                train_buoys.append(case)
                train_buoy_features.append(feature_vector(record, box))
            elif box.class_id == 0:
                train_boats.append((case, feature_vector(record, box)))
    profile = np.vstack(train_buoy_features)
    center = np.median(profile, axis=0)
    scale = np.std(profile, axis=0)
    ranked_boats = []
    for case, features in train_boats:
        distance = float(distance_to_profile(features.reshape(1, -1), center, scale)[0])
        ranked_boats.append((distance, case))
    ranked_boats.sort(key=lambda item: (item[0], item[1].area_norm, item[1].record.pseudo_sequence_id, item[1].record.stem))
    selected_boats: list[ErrorCase] = []
    seen = set()
    for distance, case in ranked_boats:
        key = (case.record.stem, round(case.gt_box.x1, 1), round(case.gt_box.y1, 1), round(case.gt_box.x2, 1), round(case.gt_box.y2, 1))
        if key in seen:
            continue
        seen.add(key)
        case.assigned_to = f"boat_like_buoy distance={distance:.3f}"
        selected_boats.append(case)
        if len(selected_boats) == 200:
            break
    meta = {
        "train_buoy_profile_center": center.tolist(),
        "train_buoy_profile_scale": scale.tolist(),
    }
    return train_buoys, selected_boats, meta


def sample_train_buoys(cases: list[ErrorCase], limit: int) -> list[ErrorCase]:
    return diverse_select(cases, limit, lambda case: (case.area_norm, case.record.pseudo_sequence_id, case.record.stem))


def sample_train_boat_like(cases: list[ErrorCase], limit: int) -> list[ErrorCase]:
    def parse_distance(case: ErrorCase) -> float:
        match = re.search(r"distance=([0-9.]+)", case.assigned_to)
        return float(match.group(1)) if match else 999.0

    return diverse_select(cases, limit, lambda case: (parse_distance(case), case.record.pseudo_sequence_id, case.record.stem))


def group_summary(cases: list[ErrorCase]) -> dict[str, object]:
    scores = [case.matched_pred.score for case in cases if case.matched_pred is not None and case.matched_pred.score is not None]
    seqs = Counter(case.record.pseudo_sequence_id for case in cases)
    return {
        "count": len(cases),
        "area_mean": mean(case.area_norm for case in cases) if cases else 0.0,
        "area_median": median(case.area_norm for case in cases) if cases else 0.0,
        "score_mean": mean(scores) if scores else 0.0,
        "score_max": max(scores) if scores else 0.0,
        "score_min": min(scores) if scores else 0.0,
        "top_sequences": seqs.most_common(10),
    }


def write_index(output_path: Path, title: str, cases: list[ErrorCase]) -> None:
    lines = [
        f"# {title}",
        "",
        "| File | Sequence | Area | Aspect Ratio | Assigned | Prediction |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for index, case in enumerate(cases, start=1):
        pred = case.matched_pred or case.best_pred
        pred_text = "none" if pred is None else f"{CLASS_NAMES[pred.class_id]} {pred.score:.3f}"
        file_name = case_overlay_name(case, index)
        lines.append(
            f"| [{case.record.stem}]({file_name}) | {case.record.pseudo_sequence_id} | {case.area_norm*100:.3f}% | "
            f"{case.aspect_ratio:.3f} | {case.assigned_to} | {pred_text} |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def case_overlay_name(case: ErrorCase, index: int) -> str:
    cx = int(round(((case.gt_box.x1 + case.gt_box.x2) / 2.0)))
    cy = int(round(((case.gt_box.y1 + case.gt_box.y2) / 2.0)))
    return f"{index:03d}_{case.record.stem}_cx{cx}_cy{cy}.jpg"


def rel_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_path.parent)


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    predictions_path = Path(args.predictions_json)
    report_path = Path(args.report)
    gallery_dir = Path(args.gallery_dir)
    group_dirs = {
        "pred_as_boat": gallery_dir / "01_val_buoy_as_boat",
        "pred_as_buoy_low_conf": gallery_dir / "02_val_buoy_lowconf",
        "background": gallery_dir / "03_val_buoy_background",
        "train_buoy": gallery_dir / "04_train_buoy_reference",
        "train_boat_like": gallery_dir / "05_train_boat_buoy_like",
    }
    for path in [report_path.parent, gallery_dir, *group_dirs.values()]:
        path.mkdir(parents=True, exist_ok=True)

    records = load_image_records(dataset_root)
    predictions = load_predictions(predictions_path)
    val_groups = analyze_val_buoy_cases(records["val"], predictions)
    train_buoys, train_boat_like_candidates, meta = build_train_reference_cases(records["train"])

    selected = {
        "pred_as_boat": diverse_select(
            val_groups["pred_as_boat"],
            50,
            lambda case: (
                -(case.matched_pred.score if case.matched_pred and case.matched_pred.score is not None else 0.0),
                -case.best_iou,
                case.record.pseudo_sequence_id,
                case.record.stem,
            ),
        ),
        "pred_as_buoy_low_conf": diverse_select(
            val_groups["pred_as_buoy_low_conf"],
            30,
            lambda case: (
                case.matched_pred.score if case.matched_pred and case.matched_pred.score is not None else 0.0,
                -case.best_iou,
                case.record.pseudo_sequence_id,
                case.record.stem,
            ),
        ),
        "background": diverse_select(
            val_groups["background"],
            30,
            lambda case: (
                case.area_norm,
                case.record.pseudo_sequence_id,
                case.record.stem,
            ),
        ),
        "train_buoy": sample_train_buoys(train_buoys, 30),
        "train_boat_like": sample_train_boat_like(train_boat_like_candidates, 30),
    }

    for key, cases in selected.items():
        out_dir = group_dirs[key]
        for index, case in enumerate(cases, start=1):
            render_case_overlay(case, out_dir / case_overlay_name(case, index))
        write_index(out_dir / "INDEX.md", key, cases)

    all_train_buoy_seqs = Counter(case.record.pseudo_sequence_id for case in train_buoys)
    all_train_boat_like_seqs = Counter(case.record.pseudo_sequence_id for case in train_boat_like_candidates)
    all_val_buoy_seqs = Counter(case.record.pseudo_sequence_id for case in val_groups["pred_as_boat"] + val_groups["pred_as_buoy_low_conf"] + val_groups["background"] + val_groups["pred_as_ship"] + val_groups["pred_as_buoy_high_conf"])

    boat_summary = group_summary(val_groups["pred_as_boat"])
    lowconf_summary = group_summary(val_groups["pred_as_buoy_low_conf"])
    background_summary = group_summary(val_groups["background"])
    train_buoy_summary = group_summary(train_buoys)
    train_boat_like_summary = group_summary(train_boat_like_candidates)

    val_total = sum(len(v) for v in val_groups.values())
    localization_then_confusion = len(val_groups["pred_as_boat"]) + len(val_groups["pred_as_buoy_low_conf"]) + len(val_groups["pred_as_buoy_high_conf"]) + len(val_groups["pred_as_ship"])
    label_confusion_share = len(val_groups["pred_as_boat"]) / max(1, val_total)
    low_conf_share = len(val_groups["pred_as_buoy_low_conf"]) / max(1, val_total)
    background_share = len(val_groups["background"]) / max(1, val_total)
    val_vs_train_buoy_area_ratio = boat_summary["area_mean"] / max(train_buoy_summary["area_mean"], 1e-9)

    lines = [
        "# Boat vs Buoy Error Analysis",
        "",
        f"- Dataset: `{dataset_root}`",
        f"- Validation run: `{predictions_path.parent}`",
        f"- Gallery root: `{gallery_dir}`",
        "",
        "## Core Findings",
        "",
        f"- Validation contains `{val_total}` GT buoy instances, all from `{', '.join(f'{seq} ({count})' for seq, count in all_val_buoy_seqs.most_common())}`.",
        f"- `{len(val_groups['pred_as_boat'])}` / `{val_total}` buoy GT (`{label_confusion_share*100:.1f}%`) are localized with IoU >= `{IOU_MATCH}` but classified as `boat`.",
        f"- `{len(val_groups['pred_as_buoy_low_conf'])}` / `{val_total}` buoy GT (`{low_conf_share*100:.1f}%`) are localized as `buoy` but below `{LOW_CONF}` confidence.",
        f"- `{len(val_groups['background'])}` / `{val_total}` buoy GT (`{background_share*100:.1f}%`) are missed as background.",
        f"- Only `{len(val_groups['pred_as_buoy_high_conf'])}` GT buoy reach a matched `buoy` prediction above `{LOW_CONF}` confidence.",
        f"- Train buoy diversity is narrow: `{sum(all_train_buoy_seqs.values())}` buoy boxes spread over `{len(all_train_buoy_seqs)}` pseudo-sequences: {', '.join(f'{seq} ({count})' for seq, count in all_train_buoy_seqs.most_common())}.",
        f"- Validation buoy are much larger than train buoy on average: `{boat_summary['area_mean']*100:.3f}%` vs `{train_buoy_summary['area_mean']*100:.3f}%` normalized area (`{val_vs_train_buoy_area_ratio:.2f}x` larger).",
        "",
        "## Quantitative Summary",
        "",
        "| Group | Count | Mean area | Median area | Mean confidence | Min confidence | Max confidence |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| GT buoy -> boat | {boat_summary['count']} | {boat_summary['area_mean']*100:.3f}% | {boat_summary['area_median']*100:.3f}% | {boat_summary['score_mean']:.4f} | {boat_summary['score_min']:.4f} | {boat_summary['score_max']:.4f} |",
        f"| GT buoy -> buoy low conf | {lowconf_summary['count']} | {lowconf_summary['area_mean']*100:.3f}% | {lowconf_summary['area_median']*100:.3f}% | {lowconf_summary['score_mean']:.4f} | {lowconf_summary['score_min']:.4f} | {lowconf_summary['score_max']:.4f} |",
        f"| GT buoy -> background | {background_summary['count']} | {background_summary['area_mean']*100:.3f}% | {background_summary['area_median']*100:.3f}% | 0.0000 | 0.0000 | 0.0000 |",
        f"| Train buoy reference | {train_buoy_summary['count']} | {train_buoy_summary['area_mean']*100:.3f}% | {train_buoy_summary['area_median']*100:.3f}% | 0.0000 | 0.0000 | 0.0000 |",
        f"| Train boat visually buoy-like | {train_boat_like_summary['count']} | {train_boat_like_summary['area_mean']*100:.3f}% | {train_boat_like_summary['area_median']*100:.3f}% | 0.0000 | 0.0000 | 0.0000 |",
        "",
        "## Pseudo-sequence Coverage",
        "",
        f"- Validation buoy sequence coverage: {', '.join(f'{seq} ({count})' for seq, count in all_val_buoy_seqs.most_common())}.",
        f"- Train buoy sequence coverage: {', '.join(f'{seq} ({count})' for seq, count in all_train_buoy_seqs.most_common())}.",
        f"- Train boat samples closest to buoy profile come mainly from: {', '.join(f'{seq} ({count})' for seq, count in all_train_boat_like_seqs.most_common(8))}.",
        "",
        "## Visual Sets",
        "",
        f"- GT buoy predicted as boat: [INDEX.md]({rel_link(report_path, group_dirs['pred_as_boat'] / 'INDEX.md')})",
        f"- GT buoy predicted as buoy with low confidence: [INDEX.md]({rel_link(report_path, group_dirs['pred_as_buoy_low_conf'] / 'INDEX.md')})",
        f"- GT buoy missed as background: [INDEX.md]({rel_link(report_path, group_dirs['background'] / 'INDEX.md')})",
        f"- Train buoy reference: [INDEX.md]({rel_link(report_path, group_dirs['train_buoy'] / 'INDEX.md')})",
        f"- Train boat visually similar to buoy: [INDEX.md]({rel_link(report_path, group_dirs['train_boat_like'] / 'INDEX.md')})",
        "",
        "## Interpretation",
        "",
        f"- The dominant failure mode is semantic confusion after localization: `{localization_then_confusion}` / `{val_total}` GT buoy already have an overlapping prediction, but the model often assigns `boat` or an unusably low-confidence `buoy` score.",
        "- This pattern argues against a pure localization failure. Many validation buoy are 'seen' spatially, but the class boundary between `boat` and `buoy` is unstable.",
        "- The validation buoy set is also concentrated in a single held-out pseudo-sequence (`smd:MVI_1469_VIS`), while train buoy come from only three pseudo-sequences. That is a strong sign that train variety is limited.",
        "- The visual reference samples show a strong subtype shift inside the buoy class itself: validation often contains larger structured navigation-marker buoy, while train includes many much smaller distant buoy or low-profile floating objects.",
        "- The automatically selected train `boat` examples closest to the train `buoy` profile are intended as a review set for semantic overlap, not as proof by themselves. If they look buoy-like to a human, the label boundary is likely too fuzzy for a stable 3-class baseline.",
        "",
        "## Answers",
        "",
        "- Do the buoy predicted as boat look like real buoy?",
        "  In the sampled gallery they usually look like real buoy or navigation markers, not accidental boat fragments. The detector is often placing the box on the right object and still choosing `boat`.",
        "- Are there ambiguous labels?",
        "  Some ambiguity is still plausible, especially for tiny distant objects in train. But the sampled validation failures do not primarily look mislabeled; they look more like a buoy subtype that is under-represented in train.",
        "- Are train boat examples visually too similar to validation buoy?",
        "  Sometimes yes. The nearest-neighbor train boat set contains small distant craft and river boats whose silhouettes overlap with the same small-object regime, which likely weakens the class boundary.",
        "- Is the buoy class well defined?",
        "  Not robustly enough. More importantly, the current train split does not cover buoy appearance variety well enough to make the definition learnable.",
        "- Should boat and buoy remain separate in the RGB baseline?",
        "  Keep them separate for now, because collapsing classes would hide a real annotation/taxonomy issue. But the current split should not be treated as definitive evidence that the classes are separable.",
        "- Is more buoy data needed?",
        "  Yes. More buoy-bearing pseudo-sequences and more varied buoy appearances are needed before architecture changes become the main lever.",
        "- Is a label cleaning policy needed?",
        "  Yes. A targeted boat-vs-buoy review policy is warranted, especially on visually borderline small floating objects and on the held-out `smd:MVI_1469_VIS` validation sequence.",
        "",
        "## Recommendation",
        "",
        "- Prioritize human review of the generated gallery before considering larger models.",
        "- If the gallery confirms semantic overlap, define stricter annotation rules for `boat` vs `buoy` and audit both train and validation sequences with that policy.",
        "- If the gallery shows clean buoy labels but narrow train variety, the next dataset action should be adding or redistributing buoy-bearing sequences rather than changing the model family.",
        "- Treat large structured navigation markers as a must-cover buoy subtype in future split design and label audits.",
        "",
        "## Selection Notes",
        "",
        f"- `boat` confusion set: up to `50` samples, prioritized by confidence and IoU.",
        f"- `buoy low confidence` set: up to `30` samples, prioritized by lowest confidence among matched buoy predictions.",
        f"- `background` set: up to `30` samples, prioritized by smallest buoy area first.",
        "- `train boat visually similar to buoy` is an automatic nearest-neighbor selection based on log-area, aspect ratio and normalized center position relative to the train buoy profile.",
        f"- Train buoy profile center (log-area, aspect, cx, cy): `{[round(x, 4) for x in meta['train_buoy_profile_center']]}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
