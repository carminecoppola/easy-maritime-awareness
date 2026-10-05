#!/usr/bin/env python3
# EASY Maritime Awareness - model repository
# Copyright (c) 2026 Carmine Coppola and EASY contributors.
# SPDX-License-Identifier: BSD-3-Clause
"""Train YOLOv8n on a sequence-safe split candidate and evaluate it on its test set.

The hyper-parameters are copied from the official EASY-v1 training
(``training_request.json`` of the ``yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced``
run), so the only variable that changes is the data split, not the training recipe.
After training, the best weights are evaluated explicitly on the ``test`` split and a
``test_metrics_summary.json`` is written next to them.

Usage:
    python scripts/validation/train_sequence_safe_candidate.py \
        --dataset-yaml data/processed/EASY-v3-sequence-safe-candidate/dataset.yaml \
        --project outputs/experiments/easy_v3_sequence_safe_candidate \
        --name yolov8n_pretrained_50ep_easy_v3_sequence_safe_candidate

Requires the ``ultralytics`` package (see requirements-training.txt) and, for a
reasonable training time, a GPU. The Slurm launchers next to this file show how it
was run on a cluster.
"""

import argparse
import json
from datetime import datetime, timezone

from ultralytics import YOLO


def parse_args():
    """Parse the command line."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset-yaml", required=True)
    p.add_argument("--model", default="models/pretrained/yolov8n.pt")
    p.add_argument("--project", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", default=-1)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--device", default="0")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--patience", type=int, default=20)
    p.add_argument("--cache", default="disk")
    return p.parse_args()


def main():
    """Train, evaluate on the test split and write the metrics summary."""
    args = parse_args()

    request = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_yaml": args.dataset_yaml,
        "model": args.model,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "device": args.device,
        "project": args.project,
        "name": args.name,
        "seed": args.seed,
        "patience": args.patience,
        "cache": args.cache,
        "pretrained": True,
        "note": "Same hyper-parameters as the official EASY-v1-rgb3-buoy-rebalanced training; the only variable is the data split.",
    }
    print(json.dumps(request, indent=2))

    model = YOLO(args.model)
    model.train(
        data=args.dataset_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=int(args.batch) if str(args.batch).lstrip("-").isdigit() else args.batch,
        workers=args.workers,
        device=args.device,
        seed=args.seed,
        patience=args.patience,
        cache=args.cache,
        project=args.project,
        name=args.name,
        # exist_ok prevents a previous run with the same project/name from creating a
        # "-2" suffixed directory and making the evaluation point at old weights.
        exist_ok=True,
        pretrained=True,
    )

    save_dir = str(model.trainer.save_dir)
    best_weights = f"{save_dir}/weights/best.pt"

    # val() uses the "val" split by default: run an explicit second pass on "test".
    trained = YOLO(best_weights)
    test_metrics = trained.val(data=args.dataset_yaml, split="test", imgsz=args.imgsz, project=args.project, name=f"{args.name}_test_eval", exist_ok=True)

    summary = {
        "weights": best_weights,
        "test_precision": float(test_metrics.box.mp),
        "test_recall": float(test_metrics.box.mr),
        "test_map50": float(test_metrics.box.map50),
        "test_map50_95": float(test_metrics.box.map),
    }
    with open(f"{save_dir}/test_metrics_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
