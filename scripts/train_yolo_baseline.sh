#!/bin/bash
# train_yolo_baseline.sh - Train YOLO baseline model

set -e

echo "=================================="
echo "YOLO Baseline Training"
echo "=================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

# Check if dataset exists
echo -e "${BLUE}Checking dataset...${NC}"
if [ ! -f "data/processed/EASY-v0/dataset.yaml" ]; then
    echo -e "${RED}✗ dataset.yaml not found${NC}"
    echo "Run: bash scripts/prepare_easy_v0.sh"
    exit 1
fi
echo -e "${GREEN}✓ Dataset found${NC}"

# Check GPU availability
echo -e "${BLUE}Checking GPU...${NC}"
python3 << 'PYTHON_SCRIPT'
import torch
if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("Warning: No GPU detected, using CPU (training will be slow)")
PYTHON_SCRIPT

# Start training
echo ""
echo -e "${BLUE}Starting YOLO training...${NC}"
python3 << 'PYTHON_SCRIPT'
from ultralytics import YOLO
import yaml
from pathlib import Path

# Load configuration
with open("configs/train_yolo.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create or load model
model_config = config["model"]
model = YOLO(model_config["pretrained_weights"])

# Training parameters
training_config = config["training"]
output_config = config["output"]

print(f"Model: {model_config['architecture']}-{model_config['size']}")
print(f"Epochs: {training_config['epochs']}")
print(f"Batch size: {training_config['batch_size']}")
print(f"Image size: {training_config['imgsz']}")
print()

# Train model
results = model.train(
    data="data/processed/EASY-v0/dataset.yaml",
    epochs=training_config["epochs"],
    imgsz=training_config["imgsz"],
    batch=training_config["batch_size"],
    device=training_config["device"],
    workers=training_config["workers"],
    project=output_config["project"],
    name=output_config["name"],
    save=output_config["save"],
    save_period=output_config["save_period"],
    conf=output_config["conf_threshold"],
    patience=20,  # Early stopping
    verbose=True
)

print("\n✓ Training complete!")
print(f"Results saved to: outputs/{output_config['name']}/")
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}=================================="
echo "Training complete!"
echo "==================================${NC}"
echo ""
echo "Model and results saved to: outputs/yolo_baseline/"
echo "Best model: outputs/yolo_baseline/weights/best.pt"
echo ""
