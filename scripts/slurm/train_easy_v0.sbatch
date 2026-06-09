#!/bin/bash
#SBATCH --job-name=easy-train-v0
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=low-gn
#SBATCH --gres=gpu:1

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
VENV_PYTHON="${VENV_PYTHON:-$PROJECT_ROOT/venv/bin/python}"
PATHS_CONFIG="${PATHS_CONFIG:-$PROJECT_ROOT/configs/paths.yaml}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/data}"
DATASET_YAML="${DATASET_YAML:-$DATA_ROOT/processed/EASY-v0/dataset.yaml}"
MPLCONFIGDIR="${MPLCONFIGDIR:-$PROJECT_ROOT/.cache/matplotlib}"
YOLO_CONFIG_DIR="${YOLO_CONFIG_DIR:-$PROJECT_ROOT/.cache/ultralytics}"

MODEL="${MODEL:-yolov8n.yaml}"
EPOCHS="${EPOCHS:-50}"
IMGSZ="${IMGSZ:-640}"
BATCH="${BATCH:-16}"
WORKERS="${WORKERS:-8}"
DEVICE="${DEVICE:-0}"
PROJECT_DIR="${PROJECT_DIR:-$PROJECT_ROOT/outputs/training}"
RUN_NAME="${RUN_NAME:-easy_v0_baseline}"
SEED="${SEED:-42}"
PATIENCE="${PATIENCE:-20}"
CACHE_MODE="${CACHE_MODE:-disk}"
PRETRAINED="${PRETRAINED:-0}"
RESUME="${RESUME:-0}"

cd "$PROJECT_ROOT"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[EASY] missing venv python at $VENV_PYTHON" >&2
  exit 2
fi

if [[ ! -f "$DATASET_YAML" ]]; then
  echo "[EASY] missing dataset yaml at $DATASET_YAML" >&2
  exit 2
fi

mkdir -p "$PROJECT_DIR"
mkdir -p "$MPLCONFIGDIR" "$YOLO_CONFIG_DIR"
export MPLCONFIGDIR
export YOLO_CONFIG_DIR

echo "[EASY] baseline training job"
echo "[EASY] project_root=$PROJECT_ROOT"
echo "[EASY] dataset_yaml=$DATASET_YAML"
echo "[EASY] model=$MODEL"
echo "[EASY] epochs=$EPOCHS imgsz=$IMGSZ batch=$BATCH workers=$WORKERS"
echo "[EASY] device=$DEVICE partition=${SLURM_JOB_PARTITION:-unknown}"
echo "[EASY] output=$PROJECT_DIR/$RUN_NAME"

CMD=(
  "$VENV_PYTHON" -m src.train_easy_v0
  --paths-path "$PATHS_CONFIG"
  --dataset-yaml "$DATASET_YAML"
  --model "$MODEL"
  --epochs "$EPOCHS"
  --imgsz "$IMGSZ"
  --batch "$BATCH"
  --workers "$WORKERS"
  --device "$DEVICE"
  --project "$PROJECT_DIR"
  --name "$RUN_NAME"
  --seed "$SEED"
  --patience "$PATIENCE"
  --cache "$CACHE_MODE"
)

if [[ "$PRETRAINED" == "1" ]]; then
  CMD+=(--pretrained)
fi

if [[ "$RESUME" == "1" ]]; then
  CMD+=(--resume)
fi

"${CMD[@]}"
