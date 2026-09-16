#!/bin/bash
#SBATCH --job-name=easy_v3_aboships_train
#SBATCH --partition=h100gpu
#SBATCH --nodelist=gn05
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=10:00:00
#SBATCH --output=/home/c.coppola/projects/EASY/easy-maritime-awareness/logs/slurm/easy_v3_aboships_train_%j.out
#SBATCH --error=/home/c.coppola/projects/EASY/easy-maritime-awareness/logs/slurm/easy_v3_aboships_train_%j.err

set -euo pipefail

# NOTE: REPO/VENV below are hardcoded to this cluster user's home and to
# a venv kept under the gitignored archive/ dir. Adjust both before running
# as a different user, or move the venv out of archive/ so it survives an
# archive cleanup.

REPO=/home/c.coppola/projects/EASY/easy-maritime-awareness
VENV="$REPO/archive/easy_v1_legacy_backup/root/venv"

cd "$REPO"

"$VENV/bin/python3" scripts/validation/train_sequence_safe_candidate.py \
  --dataset-yaml "$REPO/data/processed/EASY-v3-aboships-candidate/dataset.yaml" \
  --model "$REPO/models/pretrained/yolov8n.pt" \
  --project "$REPO/outputs/experiments/easy_v3_aboships_candidate" \
  --name yolov8n_pretrained_50ep_easy_v3_aboships_candidate
