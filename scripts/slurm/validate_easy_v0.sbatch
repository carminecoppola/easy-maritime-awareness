#!/bin/bash
#SBATCH --job-name=easy-validate-v0
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=compute

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
PATHS_CONFIG="${PATHS_CONFIG:-$PROJECT_ROOT/configs/paths.yaml}"

cd "$PROJECT_ROOT"

echo "[EASY] validate_easy_v0 lightweight job"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "PATHS_CONFIG=$PATHS_CONFIG"
echo "EASY_DATA_ROOT=${EASY_DATA_ROOT:-unset}"

python3 -m src.datasets.validate_easy_v0 \
  --mode processed-layout \
  --paths-path "$PATHS_CONFIG"
