#!/bin/bash
# setup_project.sh - Initialize EASY project environment

set -e

echo "=================================="
echo "EASY Project Setup Script"
echo "=================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Create Python virtual environment
echo -e "${BLUE}[1/5] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    # Use Python 3.11 or fallback to python3
    PYTHON_BIN="python3.11"
    if ! command -v $PYTHON_BIN &> /dev/null; then
        PYTHON_BIN="python3"
    fi
    $PYTHON_BIN -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# 2. Install Python dependencies
echo -e "${BLUE}[2/5] Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# 3. Create directory structure
echo -e "${BLUE}[3/5] Verifying directory structure...${NC}"
mkdir -p data/{raw,interim,processed/EASY-v0/{images/{train,val,test},labels/{train,val,test}},external}
mkdir -p src/{datasets,training,inference,visualization,utils}
mkdir -p notebooks
mkdir -p models/{pretrained,checkpoints,exported}
mkdir -p outputs/{figures,metrics,predictions,logs}
mkdir -p scripts docs tests
echo -e "${GREEN}✓ Directory structure verified${NC}"

# 4. Download pretrained YOLO models (optional)
echo -e "${BLUE}[4/5] Setting up pretrained models...${NC}"
mkdir -p models/pretrained
echo "Models will be downloaded automatically on first use by ultralytics"
echo -e "${GREEN}✓ Model directory ready${NC}"

# 5. Setup git hooks (optional)
echo -e "${BLUE}[5/5] Project setup complete!${NC}"

echo ""
echo -e "${GREEN}=================================="
echo "Setup Complete!"
echo "==================================${NC}"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Explore datasets: jupyter lab notebooks/01_dataset_exploration.ipynb"
echo "3. Check documentation: docs/project_plan.md"
echo "4. Review configuration: configs/paths.yaml"
echo ""
