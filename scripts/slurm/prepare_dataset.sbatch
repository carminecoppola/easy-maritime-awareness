#!/bin/bash
#SBATCH --job-name=easy-prepare-dataset
#SBATCH --output=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-prepare-dataset/%x-%j.out
#SBATCH --error=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-prepare-dataset/%x-%j.err
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=compute

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
VENV_PYTHON="${VENV_PYTHON:-$PROJECT_ROOT/venv/bin/python}"
PATHS_CONFIG="${PATHS_CONFIG:-$PROJECT_ROOT/configs/paths.yaml}"
SCHEMA_PATH="${SCHEMA_PATH:-$PROJECT_ROOT/configs/dataset_schema.yaml}"
DATASET="${DATASET:-smd}"
OUTPUT_MANIFEST="${OUTPUT_MANIFEST:-}"

cd "$PROJECT_ROOT"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[EASY] missing venv python at $VENV_PYTHON" >&2
  exit 2
fi

case "$DATASET" in
  smd|seaships|massmind) ;;
  *)
    echo "[EASY] unsupported DATASET=$DATASET (allowed: smd, seaships, massmind)" >&2
    exit 2
    ;;
esac

echo "[EASY] prepare dataset manifest job"
echo "[EASY] dataset: $DATASET"
"$VENV_PYTHON" -m src.datasets.generate_dataset_manifest \
  --dataset "$DATASET" \
  --paths-path "$PATHS_CONFIG" \
  --schema-path "$SCHEMA_PATH" \
  ${OUTPUT_MANIFEST:+--output "$OUTPUT_MANIFEST"}
