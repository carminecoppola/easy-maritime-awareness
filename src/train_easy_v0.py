"""
Minimal balanced-v2 training entrypoint built around Ultralytics YOLO.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Keep third-party runtime caches inside the repository workspace so the
# training job does not depend on cluster-specific home directory settings.
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("YOLO_CONFIG_DIR", str(PROJECT_ROOT / ".cache" / "ultralytics"))

from ultralytics import YOLO


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO baseline on EASY-v0-rgb3-balanced-v2")
    parser.add_argument(
        "--dataset-yaml",
        default=str(PROJECT_ROOT / "data" / "processed" / "EASY-v0-rgb3-balanced-v2" / "dataset.yaml"),
        help="Explicit dataset.yaml path",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.yaml",
        help="Ultralytics model source. Use a local .pt for pretrained weights or a .yaml for scratch training.",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    parser.add_argument("--batch", default="16", help='Batch size. Use "-1" for Ultralytics AutoBatch.')
    parser.add_argument("--workers", type=int, default=8, help="Dataloader workers")
    parser.add_argument("--device", default="0", help='Training device, e.g. "0", "cpu", "0,1"')
    parser.add_argument(
        "--project",
        default="outputs/runs/rgb3_balanced_v2_baseline",
        help="Ultralytics project output directory",
    )
    parser.add_argument(
        "--name",
        default="yolov8n_pretrained_50ep_balanced_v2",
        help="Run name inside the project directory",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser.add_argument("--cache", default="disk", help='Ultralytics cache mode: "False", "ram", or "disk"')
    parser.add_argument(
        "--pretrained",
        action="store_true",
        help="Ask Ultralytics to use pretrained initialization when supported by the selected model source.",
    )
    parser.add_argument("--resume", action="store_true", help="Resume a previous interrupted run")
    parser.add_argument("--require-cuda", action="store_true", help="Fail instead of falling back to CPU")
    return parser.parse_args()


def _resolve_dataset_yaml(args: argparse.Namespace) -> Path:
    return Path(args.dataset_yaml).expanduser().resolve()


def _coerce_cache_value(cache_value: str):
    normalized = str(cache_value).strip().lower()
    if normalized in {"false", "0", "no", "off"}:
        return False
    if normalized in {"true", "1", "yes", "on"}:
        return True
    return cache_value


def _coerce_batch_value(batch_value: str):
    normalized = str(batch_value).strip()
    try:
        return int(normalized)
    except ValueError:
        return float(normalized)


def _resolve_model_source(model_source: str) -> str:
    source = Path(model_source).expanduser()
    is_bare_weight_name = source.suffix == ".pt" and source.name == str(source)
    canonical_weight = PROJECT_ROOT / "models" / "pretrained" / source.name
    if is_bare_weight_name and canonical_weight.exists():
        return str(canonical_weight)
    return str(source.resolve()) if source.exists() else model_source


def _write_run_metadata(output_dir: Path, payload: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "training_request.json"
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return metadata_path


def _resolve_runtime_device(requested_device: str, require_cuda: bool = False) -> str:
    requested = str(requested_device).strip()
    if requested.lower() == "cpu":
        if require_cuda:
            raise RuntimeError("CPU device requested while --require-cuda is enabled.")
        return "cpu"

    # On this cluster the scheduler can expose a GPU while the local torch build
    # still fails CUDA initialization because of a driver/runtime mismatch.
    # Falling back explicitly keeps the job readable instead of crashing inside
    # Ultralytics with a less actionable stack trace.
    if not torch.cuda.is_available():
        if require_cuda:
            raise RuntimeError(
                "CUDA device '{}' was requested but torch.cuda.is_available() is false. "
                "Check the cluster driver and PyTorch CUDA build before training.".format(requested)
            )
        print(
            "[EASY] warning: CUDA requested as '{}' but unavailable in this runtime; "
            "falling back to CPU.".format(requested)
        )
        return "cpu"

    return requested


def main() -> None:
    args = _parse_args()
    dataset_yaml = _resolve_dataset_yaml(args)

    if not dataset_yaml.exists():
        raise FileNotFoundError(
            "dataset.yaml not found at {}. The active balanced-v2 dataset must exist before training.".format(
                dataset_yaml
            )
        )

    project_dir = Path(args.project).expanduser().resolve()
    requested_run_dir = project_dir / args.name
    model_source = _resolve_model_source(args.model)

    # Persist the exact request first, so every SLURM submission leaves a readable trace.
    metadata_path = _write_run_metadata(
        requested_run_dir,
        {
            "created_at": datetime.now().isoformat(),
            "dataset_yaml": str(dataset_yaml),
            "model": model_source,
            "requested_model": args.model,
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
            "require_cuda": args.require_cuda,
        },
    )

    print("[EASY] starting baseline training")
    print("[EASY] dataset_yaml={}".format(dataset_yaml))
    print("[EASY] project_dir={}".format(project_dir))
    print("[EASY] run_name={}".format(args.name))
    print("[EASY] model={}".format(model_source))
    print("[EASY] metadata={}".format(metadata_path))
    resolved_device = _resolve_runtime_device(args.device, require_cuda=args.require_cuda)
    print("[EASY] resolved_device={}".format(resolved_device))

    model = YOLO(model_source)
    model.train(
        data=str(dataset_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=_coerce_batch_value(args.batch),
        workers=args.workers,
        device=resolved_device,
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
