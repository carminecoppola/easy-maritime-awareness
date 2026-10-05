#!/bin/bash
# EASY Maritime Awareness - model repository
# Copyright (c) 2026 Carmine Coppola and EASY contributors.
# SPDX-License-Identifier: BSD-3-Clause
#
# Slurm launcher: train YOLOv8n on the sequence-safe + ABOships candidate dataset at 960 px.
# Submit it from the repository root:  sbatch scripts/validation/submit_train_aboships_960.sbatch
#
# The #SBATCH partition and node below describe the cluster this was run on (one H100
# GPU); change them for your own cluster. Logs go to logs/slurm/ (create it first).
# Environment variables:
#   EASY_PYTHON   Python of an environment with ultralytics installed (default: python3)
#   EASY_REPO     repository root (default: the directory sbatch was called from)
#SBATCH --job-name=easy_v3_aboships_960
#SBATCH --partition=h100gpu
#SBATCH --nodelist=gn05
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/slurm/easy_v3_aboships_960_%j.out
#SBATCH --error=logs/slurm/easy_v3_aboships_960_%j.err

set -euo pipefail

REPO="${EASY_REPO:-${SLURM_SUBMIT_DIR:-$PWD}}"
PYTHON="${EASY_PYTHON:-python3}"

cd "$REPO"

"$PYTHON" scripts/validation/train_sequence_safe_candidate.py \
  --dataset-yaml "$REPO/data/processed/EASY-v3-aboships-candidate/dataset.yaml" \
  --model "$REPO/models/pretrained/yolov8n.pt" \
  --project "$REPO/outputs/experiments/easy_v3_aboships_candidate" \
  --name yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960 \
  --imgsz 960
