#!/bin/bash
# run_inference_demo.sh - Run inference on test images

set -e

echo "=================================="
echo "YOLO Inference Demo"
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

# Check if model exists
echo -e "${BLUE}Checking for trained model...${NC}"
MODEL_PATH="models/checkpoints/best.pt"

if [ ! -f "$MODEL_PATH" ]; then
    # Try alternative path
    MODEL_PATH="outputs/yolo_baseline/weights/best.pt"
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${RED}✗ Trained model not found${NC}"
    echo "Train a model first: bash scripts/train_yolo_baseline.sh"
    exit 1
fi
echo -e "${GREEN}✓ Model found: $MODEL_PATH${NC}"

# Check if test images exist
echo -e "${BLUE}Looking for test images...${NC}"
TEST_DIR="data/processed/EASY-v0/images/test"

if [ ! -d "$TEST_DIR" ] || [ -z "$(find $TEST_DIR -maxdepth 1 -type f \( -name '*.jpg' -o -name '*.png' \) 2>/dev/null)" ]; then
    echo -e "${RED}⚠ No test images found${NC}"
    echo "Using demo image for inference..."
    TEST_DIR="."
    # Create a dummy test image if needed
fi

echo -e "${GREEN}✓ Test directory: $TEST_DIR${NC}"

# Run inference
echo ""
echo -e "${BLUE}Running inference...${NC}"
python3 << 'PYTHON_SCRIPT'
from ultralytics import YOLO
from pathlib import Path

model = YOLO("outputs/yolo_baseline/weights/best.pt")

test_dir = Path("data/processed/EASY-v0/images/test")

# If test directory is empty, use raw data
if not test_dir.exists() or not list(test_dir.glob("*.*")):
    print("Test directory is empty, checking raw data...")
    test_images = list(Path("data/raw").rglob("*.jpg"))[:5]
    if not test_images:
        test_images = list(Path("data/raw").rglob("*.png"))[:5]
else:
    test_images = list(test_dir.glob("*.*"))[:20]

if not test_images:
    print("No test images found")
else:
    print(f"Found {len(test_images)} test images")
    print("\nRunning inference...")
    
    for idx, image_path in enumerate(test_images):
        print(f"  [{idx+1}/{len(test_images)}] {image_path.name}...", end=" ", flush=True)
        
        results = model(str(image_path), conf=0.5)
        
        if results:
            result = results[0]
            num_detections = len(result.boxes)
            print(f"{num_detections} detections")
            
            # Save prediction
            output_path = Path("outputs/predictions") / f"pred_{image_path.stem}.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            result.save(str(output_path))
        else:
            print("No detections")

print("\n✓ Inference complete!")
print("Predictions saved to: outputs/predictions/")
PYTHON_SCRIPT

echo ""
echo -e "${GREEN}=================================="
echo "Inference demo complete!"
echo "==================================${NC}"
echo ""
echo "Results saved to: outputs/predictions/"
echo ""
