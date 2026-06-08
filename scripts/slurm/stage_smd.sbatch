#!/bin/bash
#SBATCH --job-name=easy-stage-smd
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=compute

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
VENV_PYTHON="${VENV_PYTHON:-$PROJECT_ROOT/venv/bin/python}"
MODE="${MODE:-extract}"

DOWNLOADS_DIR="${DOWNLOADS_DIR:-$PROJECT_ROOT/data/raw/smd/downloads}"
EXTRACT_ROOT="${EXTRACT_ROOT:-$PROJECT_ROOT/data/raw/smd/source_downloads}"
VISIBLE_MANIFEST_PATH="${VISIBLE_MANIFEST_PATH:-$DOWNLOADS_DIR/smd_visible_manifest.json}"
ONBOARD_MEMBERS_PATH="${ONBOARD_MEMBERS_PATH:-$DOWNLOADS_DIR/smd_onboard_object_ready_members.txt}"
ONSHORE_MEMBERS_PATH="${ONSHORE_MEMBERS_PATH:-$DOWNLOADS_DIR/smd_onshore_object_ready_members.txt}"

SOURCE_ROOT="${SOURCE_ROOT:-$EXTRACT_ROOT}"
IMAGES_DIR="${IMAGES_DIR:-$PROJECT_ROOT/data/raw/smd/images}"
ANNOTATIONS_DIR="${ANNOTATIONS_DIR:-$PROJECT_ROOT/data/raw/smd/annotations}"
VIEW="${VIEW:-vis_onshore}"
OVERWRITE="${OVERWRITE:-0}"
MAX_SEQUENCES="${MAX_SEQUENCES:-}"
STAGE_MANIFEST_PATH="${STAGE_MANIFEST_PATH:-$PROJECT_ROOT/data/raw/smd/stage_smd_${VIEW}_manifest.json}"

cd "$PROJECT_ROOT"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[EASY] missing venv python at $VENV_PYTHON" >&2
  exit 2
fi

write_member_lists() {
  "$VENV_PYTHON" scripts/inspect_smd_downloads.py \
    --downloads-dir "$DOWNLOADS_DIR" \
    --output "$VISIBLE_MANIFEST_PATH"

  "$VENV_PYTHON" - <<PY
import json
from pathlib import Path

manifest = json.loads(Path("$VISIBLE_MANIFEST_PATH").read_text())
Path("$ONBOARD_MEMBERS_PATH").write_text(
    "\n".join(manifest["archives"]["visible_onboard"]["object_ready_member_paths"]) + "\n",
    encoding="utf-8",
)
Path("$ONSHORE_MEMBERS_PATH").write_text(
    "\n".join(manifest["archives"]["visible_onshore"]["object_ready_member_paths"]) + "\n",
    encoding="utf-8",
)
PY
}

extract_visible() {
  mkdir -p "$EXTRACT_ROOT"
  write_member_lists

  echo "[EASY] extracting visible onboard ZIP into $EXTRACT_ROOT"
  unzip -n "$DOWNLOADS_DIR/VIS_Onboard.zip" -d "$EXTRACT_ROOT" $(tr '\n' ' ' < "$ONBOARD_MEMBERS_PATH")

  if command -v unrar >/dev/null 2>&1; then
    echo "[EASY] extracting visible onshore RAR via unrar into $EXTRACT_ROOT"
    while IFS= read -r member; do
      unrar x -o- "$DOWNLOADS_DIR/VIS_Onshore.rar" "$member" "$EXTRACT_ROOT/"
    done < "$ONSHORE_MEMBERS_PATH"
  elif command -v 7z >/dev/null 2>&1; then
    echo "[EASY] extracting visible onshore RAR via 7z into $EXTRACT_ROOT"
    while IFS= read -r member; do
      7z x -aos "-o$EXTRACT_ROOT" "$DOWNLOADS_DIR/VIS_Onshore.rar" "$member"
    done < "$ONSHORE_MEMBERS_PATH"
  else
    echo "[EASY] no RAR extractor found (need unrar or 7z)" >&2
    exit 2
  fi
}

stage_intermediate() {
  CMD=(
    "$VENV_PYTHON" -m src.datasets.stage_smd
    --source-root "$SOURCE_ROOT"
    --images-dir "$IMAGES_DIR"
    --annotations-dir "$ANNOTATIONS_DIR"
    --view "$VIEW"
    --output-manifest "$STAGE_MANIFEST_PATH"
  )

  if [[ "$OVERWRITE" == "1" ]]; then
    CMD+=(--overwrite)
  fi
  if [[ -n "$MAX_SEQUENCES" ]]; then
    CMD+=(--max-sequences "$MAX_SEQUENCES")
  fi

  "${CMD[@]}"
}

case "$MODE" in
  extract)
    echo "[EASY] mode=extract"
    extract_visible
    ;;
  stage)
    echo "[EASY] mode=stage"
    stage_intermediate
    ;;
  all)
    echo "[EASY] mode=all"
    extract_visible
    stage_intermediate
    ;;
  *)
    echo "[EASY] unsupported MODE=$MODE (allowed: extract, stage, all)" >&2
    exit 2
    ;;
esac
