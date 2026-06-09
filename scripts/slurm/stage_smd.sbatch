#!/bin/bash
#SBATCH --job-name=easy-stage-smd
#SBATCH --output=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-stage-smd/%x-%j.out
#SBATCH --error=/home/c.coppola/projects/EASY/easy-maritime-awareness/outputs/logs/easy-stage-smd/%x-%j.err
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
RAR_EXTRACTOR="${RAR_EXTRACTOR:-}"

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
  if [[ -s "$VISIBLE_MANIFEST_PATH" && -s "$ONBOARD_MEMBERS_PATH" && -s "$ONSHORE_MEMBERS_PATH" ]]; then
    echo "[EASY] reusing existing visible manifest and member lists"
    return
  fi

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

detect_rar_extractor() {
  local archive_path="$1"
  local candidate=""
  local -a candidates=()

  if [[ -n "$RAR_EXTRACTOR" ]]; then
    candidates+=("$RAR_EXTRACTOR")
  fi

  candidates+=(
    "unrar"
    "$HOME/.local/bin/unrar"
    "$HOME/bin/unrar"
    "$HOME/.easy/bin/unrar"
    "7z"
    "7za"
  )

  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" ]] || continue

    if [[ "$candidate" == */* ]]; then
      [[ -x "$candidate" ]] || continue
    else
      command -v "$candidate" >/dev/null 2>&1 || continue
    fi

    case "$(basename "$candidate")" in
      unrar)
        if "$candidate" lt "$archive_path" >/dev/null 2>&1; then
          echo "$candidate"
          return 0
        fi
        ;;
      7z|7za)
        if "$candidate" l "$archive_path" >/dev/null 2>&1; then
          echo "$candidate"
          return 0
        fi
        ;;
    esac
  done

  return 1
}

extract_visible() {
  mkdir -p "$EXTRACT_ROOT"
  write_member_lists

  echo "[EASY] extracting visible onboard ZIP into $EXTRACT_ROOT"
  unzip -n "$DOWNLOADS_DIR/VIS_Onboard.zip" -d "$EXTRACT_ROOT" $(tr '\n' ' ' < "$ONBOARD_MEMBERS_PATH")

  local rar_extractor=""
  rar_extractor="$(detect_rar_extractor "$DOWNLOADS_DIR/VIS_Onshore.rar")" || {
    echo "[EASY] no working RAR extractor found for VIS_Onshore.rar" >&2
    echo "[EASY] tried RAR_EXTRACTOR, unrar, ~/bin/unrar, ~/.local/bin/unrar, ~/.easy/bin/unrar, 7z, 7za" >&2
    exit 2
  }

  case "$(basename "$rar_extractor")" in
    unrar)
      echo "[EASY] extracting visible onshore RAR via $rar_extractor into $EXTRACT_ROOT"
      while IFS= read -r member; do
        "$rar_extractor" x -o- "$DOWNLOADS_DIR/VIS_Onshore.rar" "$member" "$EXTRACT_ROOT/"
      done < "$ONSHORE_MEMBERS_PATH"
      ;;
    7z|7za)
      echo "[EASY] extracting visible onshore RAR via $rar_extractor into $EXTRACT_ROOT"
      while IFS= read -r member; do
        "$rar_extractor" x -aos "-o$EXTRACT_ROOT" "$DOWNLOADS_DIR/VIS_Onshore.rar" "$member"
      done < "$ONSHORE_MEMBERS_PATH"
      ;;
    *)
      echo "[EASY] unsupported RAR extractor: $rar_extractor" >&2
      exit 2
      ;;
  esac
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
