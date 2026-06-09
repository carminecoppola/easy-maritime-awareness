"""
Minimal EASY-v0 training entrypoint built around Ultralytics YOLO.

This module intentionally stays small:
- it resolves the canonical local dataset paths from the project config
- it validates the presence of the merged EASY-v0 dataset
- it launches one baseline training run with explicit, readable arguments
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from src.config import load_paths_config, resolve_storage_paths


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Keep third-party runtime caches inside the repository workspace so the
# training job does not depend on cluster-specific home directory settings.
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("YOLO_CONFIG_DIR", str(PROJECT_ROOT / ".cache" / "ultralytics"))

from ultralytics import YOLO


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO baseline on EASY-v0")
    parser.add_argument("--paths-path", default="configs/paths.yaml", help="Path to EASY paths config")
    parser.add_argument("--data-root", default=None, help="Optional override for dataset root")
    parser.add_argument("--dataset-yaml", default=None, help="Optional explicit dataset.yaml path")
    parser.add_argument(
        "--model",
        default="yolov8n.yaml",
        help="Ultralytics model source. Use a local .pt for pretrained weights or a .yaml for scratch training.",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--workers", type=int, default=8, help="Dataloader workers")
    parser.add_argument("--device", default="0", help='Training device, e.g. "0", "cpu", "0,1"')
    parser.add_argument("--project", default="outputs/training", help="Ultralytics project output directory")
    parser.add_argument("--name", default="easy_v0_baseline", help="Run name inside the project directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser.add_argument("--cache", default="disk", help='Ultralytics cache mode: "False", "ram", or "disk"')
    parser.add_argument(
        "--pretrained",
        action="store_true",
        help="Ask Ultralytics to use pretrained initialization when supported by the selected model source.",
    )
    parser.add_argument("--resume", action="store_true", help="Resume a previous interrupted run")
    return parser.parse_args()


def _resolve_dataset_yaml(args: argparse.Namespace) -> Path:
    if args.dataset_yaml:
        return Path(args.dataset_yaml).expanduser().resolve()

    paths_config = load_paths_config(args.paths_path)
    storage_paths = resolve_storage_paths(paths_config)

    if args.data_root:
        data_root = Path(args.data_root).expanduser().resolve()
        return data_root / "processed" / "EASY-v0" / "dataset.yaml"

    return storage_paths["easy_v0"] / "dataset.yaml"


def _coerce_cache_value(cache_value: str):
    normalized = str(cache_value).strip().lower()
    if normalized in {"false", "0", "no", "off"}:
        return False
    if normalized in {"true", "1", "yes", "on"}:
        return True
    return cache_value


def _write_run_metadata(output_dir: Path, payload: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "training_request.json"
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return metadata_path


def main() -> None:
    args = _parse_args()
    dataset_yaml = _resolve_dataset_yaml(args)

    if not dataset_yaml.exists():
        raise FileNotFoundError(
            "dataset.yaml not found at {}. Build EASY-v0 before training.".format(dataset_yaml)
        )

    project_dir = Path(args.project).expanduser().resolve()
    requested_run_dir = project_dir / args.name

    # Persist the exact request first, so every SLURM submission leaves a readable trace.
    metadata_path = _write_run_metadata(
        requested_run_dir,
        {
            "created_at": datetime.now().isoformat(),
            "dataset_yaml": str(dataset_yaml),
            "model": args.model,
            "epochs": args.epochs,
            "imgsz": args.imgsz,
            "batch": args.batch,
            "workers": args.workers,
            "device": args.device,
            "project": str(project_dir),
            "name": args.name,
            "seed": args.seed,
            "patience": args.patience,
            "cache": args.cache,
            "pretrained": args.pretrained,
            "resume": args.resume,
        },
    )

    print("[EASY] starting baseline training")
    print("[EASY] dataset_yaml={}".format(dataset_yaml))
    print("[EASY] project_dir={}".format(project_dir))
    print("[EASY] run_name={}".format(args.name))
    print("[EASY] model={}".format(args.model))
    print("[EASY] metadata={}".format(metadata_path))

    model = YOLO(args.model)
    model.train(
        data=str(dataset_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        device=args.device,
        project=str(project_dir),
        name=args.name,
        seed=args.seed,
        patience=args.patience,
        cache=_coerce_cache_value(args.cache),
        pretrained=args.pretrained,
        resume=args.resume,
        exist_ok=True,
        verbose=True,
    )


if __name__ == "__main__":
    main()
