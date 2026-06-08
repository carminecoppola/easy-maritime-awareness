#!/bin/bash
#SBATCH --job-name=easy-build-v0
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=compute

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
PATHS_CONFIG="${PATHS_CONFIG:-$PROJECT_ROOT/configs/paths.yaml}"
SCHEMA_PATH="${SCHEMA_PATH:-$PROJECT_ROOT/configs/dataset_schema.yaml}"

cd "$PROJECT_ROOT"

echo "[EASY] build_easy_v0 simulation job"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "PATHS_CONFIG=$PATHS_CONFIG"
echo "SCHEMA_PATH=$SCHEMA_PATH"
echo "EASY_DATA_ROOT=${EASY_DATA_ROOT:-unset}"

python3 -m src.datasets.build_easy_v0 \
  --simulate \
  --schema-path "$SCHEMA_PATH" \
  --paths-path "$PATHS_CONFIG"
