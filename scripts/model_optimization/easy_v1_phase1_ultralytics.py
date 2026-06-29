#!/usr/bin/env python3
"""Ultralytics-backed execution helpers for EASY-v1 Phase 1."""

import argparse
import csv
import json
import math
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import torch
import yaml
from PIL import Image, ImageDraw
from ultralytics import YOLO


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@dataclass
class BoxRecord:
    cls_id: int
    cls_name: str
    xyxy: Tuple[float, float, float, float]
    confidence: Optional[float] = None


def abspath(path: str) -> str:
    return os.path.join(ROOT, path)


def relpath(path: str) -> str:
    return os.path.relpath(path, ROOT)


def load_config(path: str) -> dict:
    with open(path, "r") as handle:
        return json.load(handle)


def load_dataset_yaml(path: str) -> dict:
    with open(path, "r") as handle:
        return yaml.safe_load(handle)


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path)


def write_json(path: str, payload: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as handle:
        handle.write(text)


def file_size_mb(path: str) -> Optional[float]:
    if not os.path.exists(path):
        return None
    return os.path.getsize(path) / float(1024 * 1024)


def fmt(value: Optional[float], digits: int = 5) -> str:
    if value is None:
        return "n/a"
    return ("%%.%df" % digits) % value


def get_names(dataset_cfg: dict) -> Dict[int, str]:
    raw = dataset_cfg["names"]
    if isinstance(raw, list):
        return {idx: name for idx, name in enumerate(raw)}
    return {int(key): value for key, value in raw.items()}


def list_images(split_dir: str, image_extensions: Iterable[str]) -> List[str]:
    valid = tuple(ext.lower() for ext in image_extensions)
    return sorted(
        os.path.join(split_dir, name)
        for name in os.listdir(split_dir)
        if os.path.splitext(name)[1].lower() in valid
    )


def yolo_to_xyxy(values: List[float], width: int, height: int) -> Tuple[float, float, float, float]:
    x_center, y_center, box_w, box_h = values
    x1 = (x_center - box_w / 2.0) * width
    y1 = (y_center - box_h / 2.0) * height
    x2 = (x_center + box_w / 2.0) * width
    y2 = (y_center + box_h / 2.0) * height
    return (x1, y1, x2, y2)


def parse_gt_boxes(label_path: str, image_size: Tuple[int, int], names: Dict[int, str]) -> List[BoxRecord]:
    width, height = image_size
    boxes: List[BoxRecord] = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, "r") as handle:
        for raw_line in handle:
            parts = raw_line.strip().split()
            if len(parts) != 5:
                continue
            cls_id = int(float(parts[0]))
            coords = [float(value) for value in parts[1:]]
            boxes.append(
                BoxRecord(
                    cls_id=cls_id,
                    cls_name=names[cls_id],
                    xyxy=yolo_to_xyxy(coords, width, height),
                    confidence=None,
                )
            )
    return boxes


def iou(box_a: Tuple[float, float, float, float], box_b: Tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0
    inter = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter
    return inter / denom if denom > 0.0 else 0.0


def area_ratio(box: Tuple[float, float, float, float], image_size: Tuple[int, int]) -> float:
    width, height = image_size
    denom = float(width * height)
    if denom <= 0:
        return 0.0
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1) / denom


def summarize_metrics(metrics, names: Dict[int, str], split: str, weights_path: str, results_dir: str) -> dict:
    global_results = list(metrics.box.mean_results())
    per_class = []
    class_maps = list(metrics.box.maps)
    for class_id in range(len(names)):
        precision, recall, map50, map95 = metrics.class_result(class_id)
        f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
        per_class.append(
            {
                "class_id": class_id,
                "class_name": names[class_id],
                "precision": float(precision),
                "recall": float(recall),
                "map50": float(map50),
                "map": float(map95),
                "f1": float(f1),
            }
        )

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "weights": relpath(weights_path),
        "split": split,
        "results_dir": relpath(results_dir),
        "box_precision": float(global_results[0]),
        "box_recall": float(global_results[1]),
        "box_map50": float(global_results[2]),
        "box_map": float(global_results[3]),
        "box_f1": float(
            0.0
            if (global_results[0] + global_results[1]) == 0
            else 2 * global_results[0] * global_results[1] / (global_results[0] + global_results[1])
        ),
        "speed": {key: float(value) for key, value in metrics.speed.items()},
        "per_class_maps": [float(value) for value in class_maps],
        "per_class": per_class,
    }


def predict_split(
    model: YOLO,
    image_paths: List[str],
    imgsz: int,
    device: int | str,
    names: Dict[int, str],
) -> List[dict]:
    predictions: List[dict] = []
    results = model.predict(
        source=image_paths,
        imgsz=imgsz,
        conf=0.001,
        iou=0.7,
        max_det=300,
        save=False,
        verbose=False,
        stream=True,
        device=device,
    )
    for index, result in enumerate(results):
        boxes = []
        if result.boxes is not None:
            xyxy_values = result.boxes.xyxy.cpu().tolist()
            conf_values = result.boxes.conf.cpu().tolist()
            cls_values = result.boxes.cls.cpu().tolist()
            for xyxy, conf, cls_id in zip(xyxy_values, conf_values, cls_values):
                cls_id_int = int(cls_id)
                boxes.append(
                    {
                        "class_id": cls_id_int,
                        "class_name": names[cls_id_int],
                        "confidence": float(conf),
                        "xyxy": [float(value) for value in xyxy],
                    }
                )
        predictions.append(
            {
                "image_path": relpath(os.path.abspath(image_paths[index])),
                "image_size": [int(result.orig_shape[1]), int(result.orig_shape[0])],
                "boxes": boxes,
            }
        )
    return predictions


def evaluate_model(
    config: dict,
    weights_path: str,
    run_name: str,
    split: str,
    imgsz: int,
    collect_predictions: bool = True,
) -> dict:
    dataset_cfg = load_dataset_yaml(abspath(config["dataset"]["dataset_yaml"]))
    names = get_names(dataset_cfg)
    image_dir = abspath(os.path.join(config["dataset"]["root"], "images", split))
    image_paths = list_images(image_dir, config["dataset"]["image_extensions"])
    results_dir = abspath(os.path.join(config["phase1_runs"]["project_dir"], run_name + "_" + split))
    ensure_dir(results_dir)

    model = YOLO(weights_path)
    metrics = model.val(
        data=abspath(config["dataset"]["dataset_yaml"]),
        split=split,
        imgsz=imgsz,
        batch=16,
        device=0,
        workers=4,
        project=abspath(config["phase1_runs"]["project_dir"]),
        name=run_name + "_" + split,
        exist_ok=True,
        plots=True,
        save_json=False,
        verbose=True,
    )
    summary = summarize_metrics(metrics, names, split, weights_path, results_dir)
    write_json(os.path.join(results_dir, "metrics_summary.json"), summary)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if collect_predictions:
        prediction_payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "weights": relpath(weights_path),
            "split": split,
            "imgsz": imgsz,
            "predictions": predict_split(model, image_paths, imgsz, 0, names),
        }
        write_json(os.path.join(results_dir, "predictions.json"), prediction_payload)
    return summary


def draw_boxes(image_path: str, gt_boxes: List[BoxRecord], pred_boxes: List[BoxRecord], output_path: str) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for box in gt_boxes:
        draw.rectangle(box.xyxy, outline=(0, 255, 0), width=3)
    for box in pred_boxes:
        draw.rectangle(box.xyxy, outline=(255, 0, 0), width=2)
    ensure_dir(os.path.dirname(output_path))
    image.save(output_path)


def greedy_match(
    gt_boxes: List[BoxRecord],
    pred_boxes: List[BoxRecord],
    match_iou: float,
) -> Tuple[List[Tuple[int, int, float]], List[int], List[int]]:
    candidate_pairs = []
    for gt_idx, gt_box in enumerate(gt_boxes):
        for pred_idx, pred_box in enumerate(pred_boxes):
            if gt_box.cls_id != pred_box.cls_id:
                continue
            overlap = iou(gt_box.xyxy, pred_box.xyxy)
            if overlap >= match_iou:
                candidate_pairs.append((overlap, gt_idx, pred_idx))
    candidate_pairs.sort(reverse=True)

    matched_gt = set()
    matched_pred = set()
    matches = []
    for overlap, gt_idx, pred_idx in candidate_pairs:
        if gt_idx in matched_gt or pred_idx in matched_pred:
            continue
        matched_gt.add(gt_idx)
        matched_pred.add(pred_idx)
        matches.append((gt_idx, pred_idx, overlap))

    unmatched_gt = [idx for idx in range(len(gt_boxes)) if idx not in matched_gt]
    unmatched_pred = [idx for idx in range(len(pred_boxes)) if idx not in matched_pred]
    return matches, unmatched_gt, unmatched_pred


def render_bucket_example(
    bucket_dir: str,
    image_path: str,
    split: str,
    suffix: str,
    gt_boxes: List[BoxRecord],
    pred_boxes: List[BoxRecord],
) -> str:
    stem = os.path.splitext(os.path.basename(image_path))[0]
    filename = "%s__%s__%s.jpg" % (split, stem, suffix)
    output_path = os.path.join(bucket_dir, filename)
    draw_boxes(abspath(image_path), gt_boxes, pred_boxes, output_path)
    return relpath(output_path)


def write_bucket_manifests(bucket_rows: Dict[str, List[List[str]]], root: str) -> None:
    for bucket, rows in bucket_rows.items():
        bucket_dir = os.path.join(root, bucket)
        ensure_dir(bucket_dir)
        manifest = os.path.join(bucket_dir, "index.csv")
        with open(manifest, "w") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "image_id",
                    "split",
                    "confidence",
                    "iou",
                    "gt_class",
                    "predicted_class",
                    "source_artifact_path",
                    "status",
                ]
            )
            for row in rows:
                writer.writerow(row)


def run_error_analysis(config: dict, prediction_paths: List[str], output_root: str) -> dict:
    dataset_cfg = load_dataset_yaml(abspath(config["dataset"]["dataset_yaml"]))
    names = get_names(dataset_cfg)
    eval_cfg = config["evaluation"]
    root = abspath(output_root)
    ensure_dir(root)

    buckets = {
        "true_positives": [],
        "false_positives": [],
        "false_negatives": [],
        "buoy_missed": [],
        "boat_buoy_confusion": [],
        "low_confidence": [],
        "difficult_samples": [],
    }

    summary = {key: 0 for key in buckets}
    for prediction_path in prediction_paths:
        with open(abspath(prediction_path), "r") as handle:
            payload = json.load(handle)
        split = payload["split"]
        for item in payload["predictions"]:
            image_path = item["image_path"]
            width, height = item["image_size"]
            label_path = os.path.join(
                config["dataset"]["root"],
                "labels",
                split,
                os.path.splitext(os.path.basename(image_path))[0] + ".txt",
            )
            gt_boxes = parse_gt_boxes(abspath(label_path), (width, height), names)
            pred_boxes = [
                BoxRecord(
                    cls_id=pred["class_id"],
                    cls_name=pred["class_name"],
                    xyxy=tuple(pred["xyxy"]),
                    confidence=pred["confidence"],
                )
                for pred in item["boxes"]
            ]

            matches, unmatched_gt, unmatched_pred = greedy_match(
                gt_boxes,
                pred_boxes,
                eval_cfg["match_iou"],
            )

            difficult = False
            if any(gt_boxes[idx].cls_name == "buoy" for idx in unmatched_gt):
                difficult = True
            if len(unmatched_pred) >= 2:
                difficult = True
            if any(area_ratio(gt.xyxy, (width, height)) < eval_cfg["difficult_small_object_area_ratio"] for gt in gt_boxes):
                difficult = True

            for gt_idx, pred_idx, overlap in matches:
                gt_box = gt_boxes[gt_idx]
                pred_box = pred_boxes[pred_idx]
                source = render_bucket_example(
                    os.path.join(root, "true_positives"),
                    image_path,
                    split,
                    "tp",
                    [gt_box],
                    [pred_box],
                )
                buckets["true_positives"].append(
                    [
                        os.path.splitext(os.path.basename(image_path))[0],
                        split,
                        fmt(pred_box.confidence, 5),
                        fmt(overlap, 5),
                        gt_box.cls_name,
                        pred_box.cls_name,
                        source,
                        "matched",
                    ]
                )
                summary["true_positives"] += 1

            for gt_idx in unmatched_gt:
                gt_box = gt_boxes[gt_idx]
                source = render_bucket_example(
                    os.path.join(root, "false_negatives"),
                    image_path,
                    split,
                    "fn_%s" % gt_box.cls_name,
                    [gt_box],
                    [],
                )
                buckets["false_negatives"].append(
                    [
                        os.path.splitext(os.path.basename(image_path))[0],
                        split,
                        "",
                        "0.00000",
                        gt_box.cls_name,
                        "",
                        source,
                        "fn",
                    ]
                )
                summary["false_negatives"] += 1
                if gt_box.cls_name == "buoy":
                    buckets["buoy_missed"].append(
                        [
                            os.path.splitext(os.path.basename(image_path))[0],
                            split,
                            "",
                            "0.00000",
                            gt_box.cls_name,
                            "",
                            source,
                            "buoy_fn",
                        ]
                    )
                    summary["buoy_missed"] += 1

            for pred_idx in unmatched_pred:
                pred_box = pred_boxes[pred_idx]
                source = render_bucket_example(
                    os.path.join(root, "false_positives"),
                    image_path,
                    split,
                    "fp_%s" % pred_box.cls_name,
                    [],
                    [pred_box],
                )
                buckets["false_positives"].append(
                    [
                        os.path.splitext(os.path.basename(image_path))[0],
                        split,
                        fmt(pred_box.confidence, 5),
                        "0.00000",
                        "",
                        pred_box.cls_name,
                        source,
                        "fp",
                    ]
                )
                summary["false_positives"] += 1
                if pred_box.confidence is not None and pred_box.confidence < eval_cfg["low_confidence_threshold"]:
                    buckets["low_confidence"].append(
                        [
                            os.path.splitext(os.path.basename(image_path))[0],
                            split,
                            fmt(pred_box.confidence, 5),
                            "0.00000",
                            "",
                            pred_box.cls_name,
                            source,
                            "low_conf",
                        ]
                    )
                    summary["low_confidence"] += 1

            for gt_box in gt_boxes:
                for pred_box in pred_boxes:
                    if {gt_box.cls_name, pred_box.cls_name} != {"boat", "buoy"}:
                        continue
                    overlap = iou(gt_box.xyxy, pred_box.xyxy)
                    if overlap < eval_cfg["boat_buoy_confusion_iou"]:
                        continue
                    source = render_bucket_example(
                        os.path.join(root, "boat_buoy_confusion"),
                        image_path,
                        split,
                        "boat_buoy_confusion",
                        [gt_box],
                        [pred_box],
                    )
                    buckets["boat_buoy_confusion"].append(
                        [
                            os.path.splitext(os.path.basename(image_path))[0],
                            split,
                            fmt(pred_box.confidence, 5),
                            fmt(overlap, 5),
                            gt_box.cls_name,
                            pred_box.cls_name,
                            source,
                            "confusion",
                        ]
                    )
                    summary["boat_buoy_confusion"] += 1
                    break

            if difficult:
                source = render_bucket_example(
                    os.path.join(root, "difficult_samples"),
                    image_path,
                    split,
                    "difficult",
                    gt_boxes,
                    pred_boxes,
                )
                buckets["difficult_samples"].append(
                    [
                        os.path.splitext(os.path.basename(image_path))[0],
                        split,
                        "",
                        "",
                        "",
                        "",
                        source,
                        "difficult",
                    ]
                )
                summary["difficult_samples"] += 1

    write_bucket_manifests(buckets, root)
    write_json(
        os.path.join(root, "summary.json"),
        {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "prediction_paths": prediction_paths,
            "summary": summary,
        },
    )
    write_text(
        os.path.join(root, "README.md"),
        "# EASY-v1 Baseline Error Analysis\n\nGenerated from fresh Phase 1 prediction artifacts.\n",
    )
    return summary


def train_experiment(config: dict, experiment_id: str) -> str:
    experiment = next(item for item in config["experiments"] if item["id"] == experiment_id)
    model_path = abspath("models/pretrained/%s.pt" % experiment["model"])
    project_dir = abspath(config["phase1_runs"]["project_dir"])
    ensure_dir(project_dir)
    train_request_path = os.path.join(project_dir, experiment["run_name"], "training_request.json")
    ensure_dir(os.path.dirname(train_request_path))
    write_json(
        train_request_path,
        {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "experiment": experiment,
            "dataset_yaml": config["dataset"]["dataset_yaml"],
            "model_path": relpath(model_path),
            "project_dir": relpath(project_dir),
        },
    )

    kwargs = {
        "data": abspath(config["dataset"]["dataset_yaml"]),
        "epochs": experiment["epochs"],
        "imgsz": experiment["imgsz"],
        "batch": -1,
        "cache": experiment["cache"],
        "device": 0,
        "workers": 4,
        "project": project_dir,
        "name": experiment["run_name"],
        "exist_ok": True,
        "pretrained": True,
        "seed": config["seed"],
        "deterministic": config["deterministic"],
        "patience": experiment["patience"],
        "plots": True,
        "save": True,
        "verbose": True,
        "close_mosaic": 10,
        "hsv_h": 0.015,
        "hsv_s": 0.7,
        "hsv_v": 0.4,
        "degrees": 0.0,
        "translate": 0.1,
        "scale": 0.5,
        "shear": 0.0,
        "perspective": 0.0,
        "flipud": 0.0,
        "fliplr": 0.5,
        "mosaic": 1.0,
        "mixup": 0.0,
        "cutmix": 0.0,
        "copy_paste": 0.0,
        "auto_augment": "randaugment",
        "erasing": 0.4,
    }
    if "augmentations" in experiment:
        kwargs.update(experiment["augmentations"])

    model = YOLO(model_path)
    model.train(**kwargs)
    return os.path.join(project_dir, experiment["run_name"], "weights", "best.pt")


def write_comparison_report(config: dict, rows_by_split: Dict[str, List[dict]]) -> None:
    lines = [
        "# EASY-v1 Experiment Comparison",
        "",
        "Generated from fresh Phase 1 evaluations.",
        "",
    ]
    for split in ["val", "test"]:
        lines.append("## %s" % split.capitalize())
        lines.append("")
        lines.append("| Run name | Model | imgsz | epochs | precision | recall | mAP50 | mAP50-95 | boat precision/recall/mAP50 | ship precision/recall/mAP50 | buoy precision/recall/mAP50 | model size | inference speed | note qualitative |")
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |")
        for row in rows_by_split.get(split, []):
            per_class = {item["class_name"]: item for item in row["metrics"]["per_class"]}
            lines.append(
                "| %s | %s | %s | %s | %s | %s | %s | %s | %s/%s/%s | %s/%s/%s | %s/%s/%s | %s MB | %s ms | %s |"
                % (
                    row["run_name"],
                    row["model"],
                    row["imgsz"],
                    row["epochs"],
                    fmt(row["metrics"]["box_precision"]),
                    fmt(row["metrics"]["box_recall"]),
                    fmt(row["metrics"]["box_map50"]),
                    fmt(row["metrics"]["box_map"]),
                    fmt(per_class["boat"]["precision"]),
                    fmt(per_class["boat"]["recall"]),
                    fmt(per_class["boat"]["map50"]),
                    fmt(per_class["ship"]["precision"]),
                    fmt(per_class["ship"]["recall"]),
                    fmt(per_class["ship"]["map50"]),
                    fmt(per_class["buoy"]["precision"]),
                    fmt(per_class["buoy"]["recall"]),
                    fmt(per_class["buoy"]["map50"]),
                    fmt(row["model_size_mb"], 2),
                    fmt(row["metrics"]["speed"].get("inference"), 2),
                    row["note"],
                )
            )
        lines.append("")
    write_text(abspath(config["outputs"]["comparison_report"]), "\n".join(lines) + "\n")


def write_baseline_full_report(config: dict) -> None:
    baseline_name = config["phase1_runs"]["baseline_eval_name"]
    project_dir = config["phase1_runs"]["project_dir"]
    val_metrics = load_metrics_json(abspath(os.path.join(project_dir, baseline_name + "_val", "metrics_summary.json")))
    test_metrics = load_metrics_json(abspath(os.path.join(project_dir, baseline_name + "_test", "metrics_summary.json")))

    lines = [
        "# EASY-v1 Baseline Full Evaluation",
        "",
        "Generated from fresh Phase 1 evaluation artifacts.",
        "",
        "## Baseline Reference",
        "",
        "- Run: `%s`" % baseline_name,
        "- Weights: `%s`" % config["baseline"]["weights"],
        "- Validation artifacts: `%s`" % os.path.join(project_dir, baseline_name + "_val"),
        "- Test artifacts: `%s`" % os.path.join(project_dir, baseline_name + "_test"),
        "",
    ]

    for title, metrics in [("Validation", val_metrics), ("Test", test_metrics)]:
        lines.extend(
            [
                "## %s Metrics" % title,
                "",
                "| Metric | Value |",
                "| --- | ---: |",
                "| Precision | %s |" % fmt(metrics["box_precision"]),
                "| Recall | %s |" % fmt(metrics["box_recall"]),
                "| mAP50 | %s |" % fmt(metrics["box_map50"]),
                "| mAP50-95 | %s |" % fmt(metrics["box_map"]),
                "| F1 | %s |" % fmt(metrics["box_f1"]),
                "",
                "| Class | Precision | Recall | mAP50 | mAP50-95 | F1 |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in metrics["per_class"]:
            lines.append(
                "| %s | %s | %s | %s | %s | %s |"
                % (
                    item["class_name"],
                    fmt(item["precision"]),
                    fmt(item["recall"]),
                    fmt(item["map50"]),
                    fmt(item["map"]),
                    fmt(item["f1"]),
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Confusion Matrices And Predictions",
            "",
            "- Validation confusion matrix: `%s`" % os.path.join(project_dir, baseline_name + "_val", "confusion_matrix.png"),
            "- Test confusion matrix: `%s`" % os.path.join(project_dir, baseline_name + "_test", "confusion_matrix.png"),
            "- Validation predictions: `%s`" % os.path.join(project_dir, baseline_name + "_val", "predictions.json"),
            "- Test predictions: `%s`" % os.path.join(project_dir, baseline_name + "_test", "predictions.json"),
            "",
        ]
    )
    write_text(abspath(config["outputs"]["baseline_report"]), "\n".join(lines))


def load_metrics_json(path: str) -> dict:
    with open(path, "r") as handle:
        return json.load(handle)


def finalize_phase1(config: dict) -> None:
    project_dir = abspath(config["phase1_runs"]["project_dir"])
    baseline_name = config["phase1_runs"]["baseline_eval_name"]
    runs = [
        {
            "run_name": baseline_name,
            "model": "YOLOv8n",
            "imgsz": 640,
            "epochs": 50,
            "weights": abspath(config["baseline"]["weights"]),
            "note": "Historical baseline retrained metrics consolidated with fresh Phase 1 eval.",
        }
    ]
    for experiment in config["experiments"]:
        runs.append(
            {
                "run_name": experiment["run_name"],
                "model": experiment["model"],
                "imgsz": experiment["imgsz"],
                "epochs": experiment["epochs"],
                "weights": os.path.join(project_dir, experiment["run_name"], "weights", "best.pt"),
                "note": experiment["notes"],
            }
        )

    rows_by_split = {"val": [], "test": []}
    ranking_rows = []
    for run in runs:
        run_test_metrics = load_metrics_json(os.path.join(project_dir, run["run_name"] + "_test", "metrics_summary.json"))
        run_val_metrics = load_metrics_json(os.path.join(project_dir, run["run_name"] + "_val", "metrics_summary.json"))
        model_size_mb = file_size_mb(run["weights"])
        for split, metrics in [("val", run_val_metrics), ("test", run_test_metrics)]:
            rows_by_split[split].append(
                {
                    "run_name": run["run_name"],
                    "model": run["model"],
                    "imgsz": run["imgsz"],
                    "epochs": run["epochs"],
                    "metrics": metrics,
                    "model_size_mb": model_size_mb,
                    "note": run["note"],
                }
            )
        per_class = {item["class_name"]: item for item in run_test_metrics["per_class"]}
        recalls = [per_class["boat"]["recall"], per_class["ship"]["recall"], per_class["buoy"]["recall"]]
        ranking_rows.append(
            {
                "run": run,
                "metrics": run_test_metrics,
                "buoy_recall": per_class["buoy"]["recall"],
                "recall_spread": max(recalls) - min(recalls),
                "map50": run_test_metrics["box_map50"],
                "map": run_test_metrics["box_map"],
                "size_mb": model_size_mb if model_size_mb is not None else math.inf,
            }
        )

    ranking_rows.sort(
        key=lambda item: (
            -item["buoy_recall"],
            item["recall_spread"],
            -item["map50"],
            -item["map"],
            item["size_mb"],
        )
    )
    winner = ranking_rows[0]
    best_weights = winner["run"]["weights"]
    final_model_path = abspath(config["phase1_runs"]["final_model_path"])
    ensure_dir(os.path.dirname(final_model_path))
    shutil.copy2(best_weights, final_model_path)

    write_comparison_report(config, rows_by_split)

    selection_lines = [
        "# EASY-v1 Model Selection",
        "",
        "## Winner",
        "",
        "- Run: `%s`" % winner["run"]["run_name"],
        "- Source weights: `%s`" % relpath(best_weights),
        "- Copied model: `%s`" % config["phase1_runs"]["final_model_path"],
        "",
        "## Ranking",
        "",
        "| Rank | Run | Buoy recall | Recall spread | mAP50 | mAP50-95 | Model size MB |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for index, row in enumerate(ranking_rows, start=1):
        selection_lines.append(
            "| %d | %s | %s | %s | %s | %s | %s |"
            % (
                index,
                row["run"]["run_name"],
                fmt(row["buoy_recall"]),
                fmt(row["recall_spread"]),
                fmt(row["map50"]),
                fmt(row["map"]),
                fmt(row["size_mb"], 2),
            )
        )
    selection_lines.extend(
        [
            "",
            "## Decision Rationale",
            "",
            "Selection order was: buoy recall, class stability, mAP50, mAP50-95, model size, Raspberry deployability.",
            "",
        ]
    )
    write_text(abspath(config["outputs"]["selection_report"]), "\n".join(selection_lines) + "\n")

    model = YOLO(final_model_path)
    exported = model.export(format="onnx", imgsz=winner["run"]["imgsz"], opset=12, simplify=True, device=0)
    final_onnx_path = abspath(config["phase1_runs"]["final_onnx_path"])
    ensure_dir(os.path.dirname(final_onnx_path))
    if os.path.abspath(exported) != os.path.abspath(final_onnx_path):
        shutil.copy2(exported, final_onnx_path)

    deployment_lines = [
        "# Deployment Notes",
        "",
        "## Export",
        "",
        "- Source model: `%s`" % config["phase1_runs"]["final_model_path"],
        "- Exported ONNX: `%s`" % config["phase1_runs"]["final_onnx_path"],
        "- Export command equivalent: `python -m ultralytics export model=%s format=onnx imgsz=%s opset=12 simplify=True`"
        % (config["phase1_runs"]["final_model_path"], winner["run"]["imgsz"]),
        "- Class mapping: `0=boat`, `1=ship`, `2=buoy`.",
        "- Preprocessing: RGB input with Ultralytics letterbox for imgsz `%s`." % winner["run"]["imgsz"],
        "- Raspberry follow-up: validate latency, RAM, and prediction parity with representative maritime frames.",
        "",
    ]
    write_text(abspath(config["outputs"]["deployment_notes"]), "\n".join(deployment_lines) + "\n")


def run_baseline_full(config: dict) -> None:
    baseline_run_name = config["phase1_runs"]["baseline_eval_name"]
    weights_path = abspath(config["baseline"]["weights"])
    evaluate_model(config, weights_path, baseline_run_name, "val", 640)
    evaluate_model(config, weights_path, baseline_run_name, "test", 640)
    prediction_paths = [
        os.path.join(config["phase1_runs"]["project_dir"], baseline_run_name + "_val", "predictions.json"),
        os.path.join(config["phase1_runs"]["project_dir"], baseline_run_name + "_test", "predictions.json"),
    ]
    run_error_analysis(config, prediction_paths, config["outputs"]["error_analysis_root"])
    write_baseline_full_report(config)


def rebuild_baseline_artifacts(config: dict) -> None:
    baseline_run_name = config["phase1_runs"]["baseline_eval_name"]
    prediction_paths = [
        os.path.join(config["phase1_runs"]["project_dir"], baseline_run_name + "_val", "predictions.json"),
        os.path.join(config["phase1_runs"]["project_dir"], baseline_run_name + "_test", "predictions.json"),
    ]
    for prediction_path in prediction_paths:
        if not os.path.exists(abspath(prediction_path)):
            raise FileNotFoundError("Missing baseline predictions: %s" % prediction_path)
    run_error_analysis(config, prediction_paths, config["outputs"]["error_analysis_root"])
    write_baseline_full_report(config)


def run_experiment_full(config: dict, experiment_id: str) -> None:
    experiment = next(item for item in config["experiments"] if item["id"] == experiment_id)
    best_weights = train_experiment(config, experiment_id)
    evaluate_model(config, best_weights, experiment["run_name"], "val", experiment["imgsz"], collect_predictions=False)
    evaluate_model(config, best_weights, experiment["run_name"], "test", experiment["imgsz"], collect_predictions=False)


def eval_experiment(config: dict, experiment_id: str) -> None:
    experiment = next(item for item in config["experiments"] if item["id"] == experiment_id)
    best_weights = os.path.join(
        abspath(config["phase1_runs"]["project_dir"]),
        experiment["run_name"],
        "weights",
        "best.pt",
    )
    if not os.path.exists(best_weights):
        raise FileNotFoundError("Missing trained weights: %s" % best_weights)
    evaluate_model(config, best_weights, experiment["run_name"], "val", experiment["imgsz"], collect_predictions=False)
    evaluate_model(config, best_weights, experiment["run_name"], "test", experiment["imgsz"], collect_predictions=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/model_optimization/easy_v1_phase1.json",
        help="Path to config JSON relative to repo root.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    subparsers.add_parser("baseline-full")
    subparsers.add_parser("rebuild-baseline-artifacts")
    experiment_parser = subparsers.add_parser("run-experiment")
    experiment_parser.add_argument("--experiment-id", required=True, choices=["A", "B", "C"])
    eval_parser = subparsers.add_parser("eval-experiment")
    eval_parser.add_argument("--experiment-id", required=True, choices=["A", "B", "C"])
    subparsers.add_parser("finalize")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(abspath(args.config))
    if args.command == "baseline-full":
        run_baseline_full(config)
    elif args.command == "rebuild-baseline-artifacts":
        rebuild_baseline_artifacts(config)
    elif args.command == "run-experiment":
        run_experiment_full(config, args.experiment_id)
    elif args.command == "eval-experiment":
        eval_experiment(config, args.experiment_id)
    elif args.command == "finalize":
        finalize_phase1(config)
    else:
        parser.error("unknown command: %s" % args.command)


if __name__ == "__main__":
    main()
