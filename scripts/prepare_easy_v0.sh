#!/bin/bash
# prepare_easy_v0.sh - Prepare EASY-v0 dataset

set -e

echo "=================================="
echo "EASY-v0 Dataset Preparation"
echo "=================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    source venv/bin/activate
fi

echo -e "${BLUE}Step 1: Verify source datasets${NC}"
for dataset in sail_o_vision marineinst massmind eranet easy_acquisition; do
    dataset_path="data/raw/$dataset"
    if [ -d "$dataset_path" ]; then
        count=$(find "$dataset_path" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l)
        echo -e "${GREEN}✓${NC} $dataset: $count images"
    else
        echo -e "${YELLOW}⚠${NC} $dataset: Not found (skipping)"
    fi
done

echo ""
echo -e "${BLUE}Step 2: Create dataset.yaml${NC}"
cat > data/processed/EASY-v0/dataset.yaml << 'EOF'
path: /path/to/EASY-v0
train: images/train
val: images/val
test: images/test

nc: 8
names: 
  0: ship
  1: boat
  2: speedboat
  3: sailboat
  4: buoy
  5: structure
  6: helicopter
  7: aircraft
EOF
echo -e "${GREEN}✓${NC} dataset.yaml created"

echo ""
echo -e "${BLUE}Step 3: Validate dataset structure${NC}"
python3 << 'PYTHON_SCRIPT'
from pathlib import Path
from src.datasets.validate_yolo_dataset import validate_yolo_dataset_structure

dataset_dir = "data/processed/EASY-v0"
dataset_path = Path(dataset_dir)

if dataset_path.exists():
    is_valid, errors = validate_yolo_dataset_structure(dataset_dir)
    
    if is_valid:
        print(f"✓ Dataset structure is valid")
    else:
        print(f"✗ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
else:
    print(f"Dataset directory not found: {dataset_dir}")
    print("Creating empty structure...")
    for split in ["train", "val", "test"]:
        (dataset_path / "images" / split).mkdir(parents=True, exist_ok=True)
        (dataset_path / "labels" / split).mkdir(parents=True, exist_ok=True)
    print("✓ Empty structure created")
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}=================================="
echo "EASY-v0 preparation complete!"
echo "==================================${NC}"
echo ""
echo "Next: Run datasets/merge_datasets.py to combine source datasets"
echo ""
