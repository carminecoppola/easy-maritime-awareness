#!/bin/bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <job.sbatch> [sbatch args...]" >&2
  exit 2
fi

JOB_SCRIPT="$1"
shift

if [[ ! -f "$JOB_SCRIPT" ]]; then
  echo "[EASY] job script not found: $JOB_SCRIPT" >&2
  exit 2
fi

JOB_NAME="$(sed -n 's/^#SBATCH --job-name=//p' "$JOB_SCRIPT" | head -n 1)"
if [[ -z "$JOB_NAME" ]]; then
  echo "[EASY] could not resolve job name from $JOB_SCRIPT" >&2
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/outputs/logs/$JOB_NAME"
mkdir -p "$LOG_DIR"

echo "[EASY] submitting $JOB_NAME"
echo "[EASY] logs: $LOG_DIR"

sbatch "$JOB_SCRIPT" "$@"
