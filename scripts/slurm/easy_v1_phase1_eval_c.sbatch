#!/bin/bash
#SBATCH --job-name=easyv1_eval_c
#SBATCH --output=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/slurm/easy_v1_phase1/logs/%x-%j.out
#SBATCH --error=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/slurm/easy_v1_phase1/logs/%x-%j.err
#SBATCH --time=36:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=low-gn
#SBATCH --gres=gpu:1

set -euo pipefail
cd /home/c.coppola/projects/EASY/easy-maritime-awareness
PYTHON_BIN=/home/c.coppola/projects/EASY/easy-maritime-awareness/archive/easy_v1_legacy_backup/root/venv/bin/python
export MPLCONFIGDIR=/tmp/easy_v1_mpl_${SLURM_JOB_ID:-local}
mkdir -p "$MPLCONFIGDIR"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing runtime python: $PYTHON_BIN"
  exit 1
fi

"$PYTHON_BIN" scripts/model_optimization/easy_v1_phase1_ultralytics.py eval-experiment --experiment-id C
