#!/bin/bash
# prepare_easy_v0.sh - Prepare EASY-v0 dataset (simulation-only wrapper)

set -e

echo "=================================="
echo "EASY-v0 Dataset Preparation"
echo "=================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "This wrapper only prepares the simulation build."
echo "No dataset download, merge, conversion, or training is executed here."
echo ""
python3 -m src.datasets.build_easy_v0 --simulate "$@"
