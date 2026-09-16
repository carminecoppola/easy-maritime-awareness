#!/usr/bin/env python3
"""Training di prova su un candidato di split sequence-safe, per confrontarlo
con EASY-v1-rgb3-buoy-rebalanced a parita' di iperparametri.

Iperparametri copiati da
`outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/training_request.json`
(il training ufficiale di EASY-v1), cosi' l'unica variabile che cambia e' lo
split dei dati, non la ricetta di training.

Uso:
    venv/bin/python scripts/validation/train_sequence_safe_candidate.py \
        --dataset-yaml data/processed/EASY-v3-sequence-safe-candidate/dataset.yaml \
        --project outputs/experiments/easy_v3_sequence_safe_candidate \
        --name yolov8n_pretrained_50ep_easy_v3_sequence_safe_candidate
"""

import argparse
import json
from datetime import datetime, timezone

from ultralytics import YOLO


def parse_args():
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
        "note": "Stessi iperparametri del training ufficiale EASY-v1-rgb3-buoy-rebalanced; unica variabile: lo split dei dati.",
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
        # exist_ok evita che una run precedente con lo stesso project/name
        # crei una directory con suffisso "-2" e faccia puntare la
        # valutazione a pesi vecchi.
        exist_ok=True,
        pretrained=True,
    )

    save_dir = str(model.trainer.save_dir)
    best_weights = f"{save_dir}/weights/best.pt"

    # val() di default usa lo split "val": secondo giro esplicito su "test".
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
