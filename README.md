# EASY: Easy Maritime Awareness

**EASY** is a comprehensive Computer Vision project focused on maritime object detection and segmentation. The project leverages public maritime datasets to build a unified dataset (EASY-v0) and train state-of-the-art detection models for future integration with Raspberry Pi edge devices equipped with RGB and FLIR cameras.

## Project Goals

1. **Dataset Analysis**: Analyze and understand public maritime datasets
   - Sail-O-Vision
   - MarineInst
   - MassMind
   - ERA-Net
   - EASY Acquisition (custom)

2. **Unified Dataset**: Construct EASY-v0, a consolidated maritime object detection benchmark

3. **Model Training**: Develop and train YOLO-based models for:
   - Object detection (ships, boats, structures)
   - Instance segmentation (water, vessels, coastal features)

4. **Edge Integration**: Prepare models for deployment on:
   - Raspberry Pi 4/5
   - RGB cameras
   - FLIR thermal cameras

## Quick Start

### Setup

```bash
# Clone repository
git clone <repo-url>
cd easy-maritime-awareness

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Project Structure

```
easy-maritime-awareness/
├── data/                          # Data storage
│   ├── raw/                       # Source datasets
│   ├── processed/EASY-v0/         # Unified dataset
│   └── external/                  # Additional resources
├── src/                           # Source code
│   ├── datasets/                  # Dataset utilities
│   ├── training/                  # Model training
│   ├── inference/                 # Prediction & deployment
│   └── visualization/             # Analysis tools
├── notebooks/                     # Jupyter notebooks
├── configs/                       # Configuration files
├── docs/                          # Documentation
├── models/                        # Model artifacts
├── outputs/                       # Results & metrics
└── scripts/                       # Shell scripts
```

## Dataset Organization

Public datasets are organized in `data/raw/`:

- `sail_o_vision/` - Sail-O-Vision dataset
- `marineinst/` - MarineInst annotations
- `massmind/` - MassMind dataset
- `eranet/` - ERA-Net data
- `easy_acquisition/` - Custom acquired data

## Roadmap

See [docs/project_plan.md](docs/project_plan.md) for detailed timeline and milestones.

### Phase 1: Foundation (Week 1-2)
- [ ] Repository setup & dataset analysis
- [ ] EASY-v0 dataset construction

### Phase 2: Training (Week 3-4)
- [ ] YOLO baseline training
- [ ] Model evaluation & error analysis

### Phase 3: Hardware Integration (Week 5-6)
- [ ] Raspberry Pi setup
- [ ] RGB camera acquisition
- [ ] FLIR thermal integration

### Phase 4: Deployment (Week 7-8)
- [ ] Model fine-tuning
- [ ] Demo application

## Key Features

- **Modular Architecture**: Organized into datasets, training, inference, and utilities modules
- **Configuration-Driven**: YAML-based configs for datasets and training parameters
- **Comprehensive Testing**: Unit tests for dataset structure validation
- **Documentation**: Detailed docs on dataset strategy, model approach, and hardware integration
- **Reproducibility**: All experiments logged with metrics and predictions saved

## Contributing

Follow the project guidelines in [docs/](docs/) when adding new features.

## License

[To be determined]

## Contact

For questions or contributions, please open an issue or PR.
