#!/usr/bin/env python3
"""Run a post-training YOLO validation pass for the active balanced-v2 workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("YOLO_CONFIG_DIR", str(PROJECT_ROOT / ".cache" / "ultralytics"))

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained YOLO weights on EASY-v0-rgb3-balanced-v2")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--dataset-yaml", default="data/processed/EASY-v0-rgb3-balanced-v2/dataset.yaml")
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    parser.add_argument("--device", default="0")
    parser.add_argument("--project", default="outputs/runs/rgb3_balanced_v2_baseline")
    parser.add_argument("--name", default="yolov8n_pretrained_50ep_balanced_v2_val")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--save-json", action="store_true")
    parser.add_argument("--save-txt", action="store_true")
    parser.add_argument("--save-conf", action="store_true")
    return parser.parse_args()


def load_class_names(dataset_yaml: str) -> dict[int, str]:
    payload = yaml.safe_load(Path(dataset_yaml).read_text(encoding="utf-8"))
    names = payload["names"]
    if isinstance(names, list):
        return {index: str(name) for index, name in enumerate(names)}
    return {int(class_id): str(name) for class_id, name in names.items()}


def f1_score(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)


def main() -> None:
    args = parse_args()
    model = YOLO(args.weights)
    metrics = model.val(
        data=args.dataset_yaml,
        split=args.split,
        device=args.device,
        project=args.project,
        name=args.name,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        plots=True,
        save_json=args.save_json,
        save_txt=args.save_txt,
        save_conf=args.save_conf,
    )
    output_dir = Path(args.project) / args.name
    output_dir.mkdir(parents=True, exist_ok=True)
    names = load_class_names(args.dataset_yaml)
    per_class = []
    for metric_index, class_id in enumerate(metrics.box.ap_class_index):
        precision, recall, map50, mean_ap = metrics.box.class_result(metric_index)
        class_id = int(class_id)
        per_class.append(
            {
                "class_id": class_id,
                "class_name": names.get(class_id, f"class_{class_id}"),
                "precision": float(precision),
                "recall": float(recall),
                "map50": float(map50),
                "map": float(mean_ap),
                "f1": f1_score(float(precision), float(recall)),
            }
        )

    summary = {
        "weights": args.weights,
        "dataset_yaml": args.dataset_yaml,
        "split": args.split,
        "results_dir": str(output_dir),
        "box_map": float(metrics.box.map),
        "box_map50": float(metrics.box.map50),
        "box_map75": float(metrics.box.map75),
        "per_class_maps": [float(value) for value in metrics.box.maps],
        "per_class": per_class,
    }
    (output_dir / "metrics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(output_dir / "metrics_summary.json")


if __name__ == "__main__":
    main()
