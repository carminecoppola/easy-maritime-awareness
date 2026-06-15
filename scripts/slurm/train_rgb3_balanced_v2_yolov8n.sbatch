#!/bin/bash
#SBATCH --job-name=easy-rgb3-balanced-v2-yolov8n
#SBATCH --output=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-rgb3-balanced-v2-yolov8n/%x-%j.out
#SBATCH --error=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-rgb3-balanced-v2-yolov8n/%x-%j.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=low-gn
#SBATCH --gres=gpu:1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-${SLURM_SUBMIT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}}"
VENV_PYTHON="${VENV_PYTHON:-$PROJECT_ROOT/venv/bin/python}"
DATASET_YAML="${DATASET_YAML:-$PROJECT_ROOT/data/processed/EASY-v0-rgb3-balanced-v2/dataset.yaml}"
MODEL_STORE="${MODEL_STORE:-$PROJECT_ROOT/models/pretrained}"
MODEL="${MODEL:-$MODEL_STORE/yolov8n.pt}"
EPOCHS="${EPOCHS:-50}"
IMGSZ="${IMGSZ:-640}"
BATCH="${BATCH:--1}"
WORKERS="${WORKERS:-4}"
DEVICE="${DEVICE:-0}"
PROJECT_DIR="${PROJECT_DIR:-$PROJECT_ROOT/outputs/runs/rgb3_balanced_v2_baseline}"
RUN_NAME="${RUN_NAME:-yolov8n_pretrained_50ep_balanced_v2}"
VAL_NAME="${VAL_NAME:-${RUN_NAME}_val}"
REPORT_DIR="${REPORT_DIR:-$PROJECT_ROOT/outputs/reports/rgb3_balanced_v2_baseline}"
REPORT_PATH="${REPORT_PATH:-$REPORT_DIR/${RUN_NAME}_report.md}"
MPLCONFIGDIR="${MPLCONFIGDIR:-$PROJECT_ROOT/.cache/matplotlib}"
YOLO_CONFIG_DIR="${YOLO_CONFIG_DIR:-$PROJECT_ROOT/.cache/ultralytics}"

cd "$PROJECT_ROOT"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[EASY] missing venv python at $VENV_PYTHON" >&2
  exit 2
fi

if [[ ! -f "$DATASET_YAML" ]]; then
  echo "[EASY] missing balanced-v2 dataset yaml at $DATASET_YAML" >&2
  exit 2
fi

if [[ ! -f "$MODEL" ]]; then
  echo "[EASY] missing model weights at $MODEL" >&2
  exit 2
fi

mkdir -p "$PROJECT_DIR" "$MPLCONFIGDIR" "$YOLO_CONFIG_DIR" "$MODEL_STORE" "$REPORT_DIR" "$(dirname "$REPORT_PATH")"
export MPLCONFIGDIR YOLO_CONFIG_DIR
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

echo "[EASY] RGB3 balanced-v2 YOLOv8n pretrained baseline"
echo "[EASY] dataset_yaml=$DATASET_YAML"
echo "[EASY] model=$MODEL"
echo "[EASY] epochs=$EPOCHS imgsz=$IMGSZ batch=$BATCH workers=$WORKERS"
echo "[EASY] device=$DEVICE partition=${SLURM_JOB_PARTITION:-unknown}"
echo "[EASY] output=$PROJECT_DIR/$RUN_NAME"
echo "[EASY] report=$REPORT_PATH"

"$VENV_PYTHON" - <<'PY'
import torch
print("[EASY] torch:", torch.__version__)
print("[EASY] cuda available:", torch.cuda.is_available())
print("[EASY] cuda device count:", torch.cuda.device_count())
if not torch.cuda.is_available():
    raise SystemExit("[EASY] CUDA is not available; refusing to start GPU baseline.")
PY

cd "$MODEL_STORE"

"$VENV_PYTHON" -m src.train_easy_v0 \
  --dataset-yaml "$DATASET_YAML" \
  --model "$MODEL" \
  --epochs "$EPOCHS" \
  --imgsz "$IMGSZ" \
  --batch "$BATCH" \
  --workers "$WORKERS" \
  --device "$DEVICE" \
  --project "$PROJECT_DIR" \
  --name "$RUN_NAME" \
  --seed 42 \
  --patience 20 \
  --cache disk \
  --pretrained \
  --require-cuda

cd "$PROJECT_ROOT"

"$VENV_PYTHON" scripts/evaluate_yolo_model.py \
  --weights "$PROJECT_DIR/$RUN_NAME/weights/best.pt" \
  --dataset-yaml "$DATASET_YAML" \
  --split val \
  --device "$DEVICE" \
  --project "$PROJECT_DIR" \
  --name "$VAL_NAME" \
  --imgsz "$IMGSZ" \
  --batch 16 \
  --workers "$WORKERS" \
  --save-json

"$VENV_PYTHON" scripts/report_rgb3_balanced_v2_baseline.py \
  --run-dir "$PROJECT_DIR/$RUN_NAME" \
  --val-summary "$PROJECT_DIR/$VAL_NAME/metrics_summary.json" \
  --output "$REPORT_PATH"
