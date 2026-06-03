# Dataset Strategy

## Overview

EASY-v0 is a unified dataset combining public maritime datasets to create a comprehensive benchmark for vessel detection and classification.

## Source Datasets

### 1. Sail-O-Vision
- **Format**: Custom
- **Focus**: Sailing vessels and maritime scenes
- **Typical classes**: Sailboats, rigging, water conditions
- **Integration**: [To be populated during dataset analysis]

### 2. MarineInst
- **Format**: COCO
- **Focus**: Marine instances and structures
- **Typical classes**: Ships, boats, structures, buoys
- **Integration**: [To be populated during dataset analysis]

### 3. MassMind
- **Format**: Custom
- **Focus**: Mass aerial and maritime observations
- **Typical classes**: Various maritime objects
- **Integration**: [To be populated during dataset analysis]

### 4. ERA-Net
- **Format**: COCO
- **Focus**: Environmental and resource awareness
- **Typical classes**: Maritime infrastructure
- **Integration**: [To be populated during dataset analysis]

### 5. EASY Acquisition
- **Format**: Custom (to be standardized)
- **Focus**: Custom acquired maritime data
- **Typical classes**: Context-specific maritime objects
- **Integration**: [To be populated during data collection]

## EASY-v0 Class Schema

Unified class taxonomy across all sources:

```
0: ship          - Large commercial/naval vessels
1: boat          - General small to medium vessels
2: speedboat     - High-speed boats
3: sailboat      - Sailing vessels
4: buoy          - Navigation buoys and markers
5: structure     - Maritime structures (docks, platforms)
6: helicopter    - Aerial vehicles
7: aircraft      - Fixed-wing aircraft
```

## Data Split Strategy

- **Training**: 70% (main learning)
- **Validation**: 15% (hyperparameter tuning, real-time feedback)
- **Test**: 15% (final evaluation)

### Split Constraints

- Maintain source dataset proportions
- Ensure class balance where possible
- Random seed for reproducibility: 42

## Format Conversion Pipeline

All source datasets converted to YOLO format:

```
images/
├── train/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── val/
└── test/

labels/
├── train/
│   ├── img_001.txt
│   ├── img_002.txt
│   └── ...
├── val/
└── test/
```

### YOLO Label Format

```
<class_id> <x_center> <y_center> <width> <height>
```

All coordinates normalized to [0, 1].

## Data Augmentation

During training:

- **Brightness/Contrast**: ±10%
- **Saturation**: ±10%
- **Hue**: ±5%
- **Flip**: Horizontal (50%)
- **Mosaic**: Enabled for context mixing

## Quality Assurance

### Validation Checks

1. **Image Integrity**
   - Check all images readable
   - Min size: 320x320
   - Max size: 2048x2048

2. **Label Consistency**
   - Every image has labels file
   - Valid class IDs (0-7)
   - Coordinates in [0, 1]

3. **Statistical Validation**
   - Class balance analysis
   - Annotation coverage
   - Duplicate detection

## Handling Class Imbalance

- Implement weighted loss functions
- Use stratified splits
- Apply class-specific augmentation
- Monitor per-class metrics

## Dataset Documentation

Each split includes:
- `data.yaml` - Dataset configuration
- `README.md` - Split-specific notes
- `statistics.json` - Detailed statistics
- `class_names.txt` - Class definitions

## Future Enhancements

1. Additional maritime scenarios (night, weather)
2. Higher resolution images
3. Multi-label annotations
4. Instance segmentation masks
5. Temporal sequences for video
