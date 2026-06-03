# EASY Project Context Document

**Version:** 1.0  
**Last Updated:** June 3, 2026  
**Status:** Active Development  
**Audience:** AI Agents, Developers, Researchers

---

## Executive Summary

EASY (Environmental Awareness by the Sea and beYond) is a university research project developing multimodal tools for marine environmental awareness and monitoring. The system integrates RGB and thermal imaging with AI-based object detection, segmentation, and tracking capabilities, designed for deployment on embedded hardware (Raspberry Pi).

---

## 1. Project Overview

### Project Name
**EASY** - Environmental Awareness by the Sea and beYond

### Project Context
University research initiative focused on developing multimodal tools for marine environmental awareness.

### Core Capabilities (Current & Future)
- ✓ RGB image acquisition
- ✓ Thermal FLIR image acquisition
- ⏳ Stereoscopic image acquisition (planned)
- ✓ Marine object detection
- ✓ Object classification
- ⏳ Image segmentation (planned)
- ⏳ Object tracking (planned)
- ⏳ Additional sensor integration (planned)

### Problem Statement
Current marine monitoring systems lack:
- Real-time multimodal awareness (RGB + Thermal)
- Automated object detection and classification
- Embedded deployment capability
- Integration of public datasets with custom data

---

## 2. Official Project Goals

The final system must be capable of:

| Goal | Description | Priority |
|------|-------------|----------|
| **Real-time Acquisition** | Capture images from real-world marine environments | P0 |
| **Object Detection** | Automatically detect marine objects in images | P0 |
| **Object Classification** | Classify detected objects accurately | P0 |
| **Image Segmentation** | Segment detected objects from background | P1 |
| **Embedded Deployment** | Operate on Raspberry Pi hardware | P0 |
| **Multimodal Fusion** | Integrate RGB and FLIR data streams | P1 |
| **Environmental Awareness** | Provide comprehensive marine situational awareness | P0 |
| **Tracking** | Track objects across video frames | P2 |

---

## 3. Available Hardware

### Current Hardware Inventory

| Hardware | Model | Quantity | Status | Purpose |
|----------|-------|----------|--------|---------|
| **Single-Board Computer** | Raspberry Pi 5 | 1 | Operational | Primary embedded platform |
| **Single-Board Computer** | Raspberry Pi 4 | 1 | Operational | Testing/Development |
| **RGB Cameras** | Arducam UC-517 | 2 | Not Integrated | Dual RGB acquisition |
| **RGB Camera Array** | Arducam CamArray UC-512 | 1 | Not Integrated | Potential stereoscopic acquisition |
| **Thermal Camera** | FLIR (model TBD) | 1 | Not Integrated | FLIR image acquisition |

### Critical Constraint

⚠️ **Hardware is NOT fully operational yet**

AI development must NOT depend on immediate hardware availability. The system architecture and model development must proceed independently using public datasets and simulation environments.

**Development Strategy:** Software-first approach with hardware integration as final validation phase.

---

## 4. Dataset Strategy

### Fundamental Principle

❌ **Do NOT build dataset exclusively from proprietary data**

✅ **Strategy: 80/20 Approach**
- **80%** Public datasets (established, peer-reviewed)
- **20%** Custom EASY-acquired data (future phases)

### Rationale
- Accelerate initial development
- Leverage existing research datasets
- Ensure reproducibility and scientific rigor
- Reserve custom data for fine-tuning and domain adaptation

### Candidate Public Datasets

| Dataset | Source | Objects | Format | Status |
|---------|--------|---------|--------|--------|
| **Sail-O-Vision** | University of Rhode Island | Sailboats, boats | Annotated Images | Candidate |
| **MarineInst** | University of Burgundy | Maritime objects | COCO, YOLO | Candidate |
| **MassMIND** | MIT | Marine debris, objects | Annotated | Candidate |
| **ERANet** | European Research | Marine vessels | COCO format | Candidate |
| **FLIR Public Datasets** | FLIR Systems | Thermal images | FLIR format | Under Review |

### EASY Dataset Versions

#### EASY-v0 (Current Target)
- **Scope:** Initial unified dataset from public sources
- **Classes:** 5 fundamental classes
- **Target Size:** 10,000+ annotated images
- **Format:** YOLO standard format
- **Split:** Train (70%), Val (15%), Test (15%)

#### EASY-v1+ (Future)
- Integration of custom-acquired EASY data
- Extended class definitions
- Domain adaptation datasets

---

## 5. Initial Target Classes

### EASY-v0 Classes (5 Classes)

| Class | Description | Priority | Rationale |
|-------|-------------|----------|-----------|
| **boat** | Small recreational boats, fishing vessels | P0 | Core maritime object |
| **ship** | Large cargo, container, tanker vessels | P0 | Core maritime object |
| **buoy** | Navigation markers, mooring buoys | P0 | Important for navigation |
| **debris** | Marine debris, floating objects | P1 | Environmental monitoring |
| **person** | Human swimmers, people in water | P1 | Safety monitoring |

### Class Addition Policy

❌ **New classes can only be added if:**
- Scientifically justified
- Supported by adequate dataset samples
- Aligned with project goals
- Approved by project leadership

This constraint prevents:
- Dataset drift
- Model complexity explosion
- Poor generalization

---

## 6. Model Strategy

### Development Phases

```
Phase 1: Object Detection (YOLOv8n)
         ↓
Phase 2: Instance Segmentation (YOLO Segmentation)
         ↓
Phase 3: Object Tracking (DeepSORT / ByteTrack)
         ↓
Phase 4: Multimodal Fusion (RGB + FLIR)
```

### Phase 1: Object Detection (Current)

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **Framework** | Ultralytics YOLO | Industry standard, well-documented |
| **Model Size** | YOLOv8n (nano) | Embedded deployment capable |
| **Task** | Object Detection | Foundational capability |
| **Input** | RGB Images | Public datasets available |
| **Output** | Bounding boxes + class probabilities | Standard format |

**Baseline Configuration:**
- Model: YOLOv8n
- Input Resolution: 640×640
- Batch Size: 32
- Epochs: 100
- Device: CUDA (training), CPU (inference)

### Phase 2: Instance Segmentation (Future)

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **Framework** | YOLO Segmentation | Natural progression from detection |
| **Model** | YOLOv8s (small) | Segmentation-ready |
| **Task** | Instance Segmentation | Object boundary delineation |
| **Trigger** | Phase 1 validation complete | Sequential dependency |

### Phase 3: Object Tracking (Future)

| Technology | Status | Rationale |
|-----------|--------|-----------|
| **DeepSORT** | Candidate | Classic approach, well-tested |
| **ByteTrack** | Candidate | Modern, efficient |

**Decision Point:** Phase 2 completion required before evaluation.

### Phase 4: Multimodal Fusion (Future)

| Component | Status | Notes |
|-----------|--------|-------|
| **RGB Stream** | Phase 1 | Object detection baseline |
| **FLIR Stream** | Future | Thermal image processing |
| **Fusion Strategy** | TBD | Early/mid/late fusion evaluation |

**Constraint:** Hardware FLIR integration required. Software framework must support dual-stream architecture.

---

## 7. Project Philosophy & Decision Rules

### Core Principles

```
Principle 1: Prefer Simple, Working Solutions
└─ No premature optimization
└─ No unnecessary abstractions
└─ Direct, testable implementations

Principle 2: Implement Only Required Components
└─ Scope management essential
└─ Avoid feature creep
└─ Focus on core functionality

Principle 3: NO Overengineering
└─ Raspberry Pi target prevents excessive complexity
└─ Resource constraints force pragmatic choices
└─ Simplicity aids maintenance

Principle 4: Every Component Must Be Testable
└─ Unit tests required for modules
└─ Integration tests for pipelines
└─ Validation metrics for models

Principle 5: Every Choice Must Be Scientifically Justified
└─ No arbitrary decisions
└─ Document design rationale
└─ Reference peer-reviewed literature
```

### Decision Framework for AI Agents

**When proposing ANY modification, agents must verify:**

```python
def validate_proposal(proposal):
    """
    Ensure all proposals align with project constraints.
    Return True only if ALL criteria pass.
    """
    
    criteria = {
        "aligns_with_goals": (
            "✓ Is this consistent with EASY objectives?"
        ),
        "adds_complexity": (
            "✗ Does this add unnecessary complexity?"
        ),
        "simpler_solution_exists": (
            "✗ Is there a simpler solution?"
        ),
        "rpi_compatible": (
            "✓ Is this compatible with Raspberry Pi?"
        ),
        "immediately_testable": (
            "✓ Can this be tested immediately?"
        ),
        "justified": (
            "✓ Is there scientific justification?"
        )
    }
    
    # All criteria must pass
    return all(criteria.values())
```

**Action:** If ANY criterion fails → REJECT proposal and document objection.

### Red Flags for Proposals

🚩 **Automatic Rejection if:**
- Adds 500+ lines of code without clear purpose
- Creates new dependency without justification
- Increases model size beyond Raspberry Pi RAM capability
- Requires manual data collection/labeling at scale
- Deviates from YOLOv8 baseline without experimentation
- Uses proprietary libraries instead of open-source
- Lacks test coverage
- Cannot be validated on current hardware

---

## 8. Repository Organization

### Directory Structure

```
easy-maritime-awareness/
├── configs/                    # Configuration files
│   ├── dataset_easy_v0.yaml   # Dataset definition
│   ├── train_yolo.yaml        # Training parameters
│   └── paths.yaml             # Path definitions
│
├── data/                       # Dataset directory
│   ├── raw/                    # Public dataset sources
│   │   ├── sail_o_vision/     
│   │   ├── marineinst/
│   │   ├── massmind/
│   │   ├── eranet/
│   │   └── easy_acquisition/   # Custom data (future)
│   ├── interim/               # Processed, intermediate formats
│   └── processed/             # Final YOLO-format datasets
│       └── EASY-v0/          # Current training dataset
│           ├── images/
│           │   ├── train/
│           │   ├── val/
│           │   └── test/
│           └── labels/
│               ├── train/
│               ├── val/
│               └── test/
│
├── docs/                       # Documentation
│   ├── EASY_PROJECT_CONTEXT.md # This document
│   ├── project_plan.md        # Timeline & milestones
│   ├── dataset_strategy.md    # Dataset details
│   ├── model_strategy.md      # Model details
│   └── hardware_integration_plan.md
│
├── models/                     # Model artifacts
│   ├── pretrained/            # Pre-trained YOLO models
│   ├── checkpoints/           # Training checkpoints
│   └── exported/              # Exported models (ONNX, TFLite)
│
├── notebooks/                  # Jupyter notebooks (minimal)
│   └── (development/analysis only)
│
├── outputs/                    # Experimental outputs
│   ├── figures/               # Plots, visualizations
│   ├── metrics/               # Evaluation metrics
│   ├── predictions/           # Model predictions
│   └── logs/                  # Training logs
│
├── scripts/                    # Automation scripts
│   ├── setup_project.sh       # Environment initialization
│   ├── prepare_easy_v0.sh     # Dataset preparation
│   ├── train_yolo_baseline.sh # Training automation
│   └── evaluate_model.sh      # Evaluation automation
│
├── src/                        # Source code (production)
│   ├── datasets/              # Dataset utilities
│   ├── training/              # Training pipelines
│   ├── inference/             # Inference engines
│   ├── visualization/         # Visualization utilities
│   └── utils/                 # Helper functions
│
├── tests/                      # Unit tests
│   ├── test_datasets.py
│   ├── test_training.py
│   └── test_inference.py
│
├── pyproject.toml             # Project metadata
├── requirements.txt           # Dependencies
├── README.md                  # Quick start guide
├── .gitignore                # Git ignore rules
└── venv/                      # Virtual environment
```

### Code Organization Rules

| Rule | Requirement |
|------|-------------|
| **Module Organization** | Each component (datasets, training, inference) in separate module |
| **Function Complexity** | Functions >50 lines need refactoring consideration |
| **Dependencies** | All imports declared in requirements.txt |
| **Configuration** | All parameters in YAML configs, not hardcoded |
| **Testing** | New modules require corresponding test files |
| **Documentation** | All functions need docstrings with purpose + usage |
| **Versioning** | Track model versions in models/ subdirectories |

---

## 9. Weekly Development Roadmap

### Timeline Overview

```
Week 1:   Repository Setup & Dataset Analysis
Week 2:   EASY-v0 Dataset Construction
Week 3:   YOLO Baseline Training
Week 4:   Evaluation & Error Analysis
Week 5:   RGB Hardware Integration
Week 6:   FLIR Hardware Integration
Week 7:   Fine-tuning & Optimization
Week 8:   Final Demonstration
```

### Detailed Milestones

#### Week 1: Foundation (Current Phase)
- ✓ Repository initialization
- ✓ Development environment setup
- ✓ Initial documentation
- → Dataset availability analysis
- → Public dataset download planning

**Deliverables:** Working dev environment, setup documentation

#### Week 2: Dataset Construction
- Merge public datasets into EASY-v0 format
- Validate YOLO annotation format
- Class distribution analysis
- Data quality checks
- Train/val/test split generation

**Deliverables:** EASY-v0 dataset (YOLO format), validation report

#### Week 3: Baseline Training
- YOLOv8n model training
- Baseline metrics establishment
- Training visualization
- Checkpoint management
- Initial model evaluation

**Deliverables:** Trained YOLOv8n model, baseline metrics

#### Week 4: Analysis & Refinement
- Error analysis
- Misclassification patterns
- Class imbalance assessment
- Data augmentation strategies
- Recommendations for improvement

**Deliverables:** Analysis report, improvement roadmap

#### Week 5: RGB Integration
- Hardware driver integration
- Image acquisition pipeline
- Real-time capture testing
- Performance profiling
- Dual-camera support

**Deliverables:** Functional RGB capture system

#### Week 6: FLIR Integration
- FLIR camera driver setup
- Thermal image preprocessing
- Dual-stream synchronization
- Hardware performance evaluation
- Capture pipeline optimization

**Deliverables:** Functional FLIR capture system

#### Week 7: Optimization & Fine-tuning
- Multi-modal feature fusion strategies
- Model compression for RPi
- Quantization evaluation
- Performance optimization
- Latency reduction

**Deliverables:** Optimized models for embedded deployment

#### Week 8: Final Demonstration
- End-to-end system integration
- Live demonstration setup
- Documentation finalization
- Code cleanup
- Knowledge transfer

**Deliverables:** Working system, final report, deployment guide

---

## 10. Technology Stack

### Core Dependencies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **ML Framework** | PyTorch | 2.12.0 | Deep learning backend |
| **Detection** | Ultralytics YOLO | 8.4.60 | Object detection models |
| **Image Processing** | OpenCV | 4.13.0 | Image I/O and preprocessing |
| **Data Processing** | NumPy, Pandas | Latest | Numerical/tabular operations |
| **Visualization** | Matplotlib, Seaborn | Latest | Results visualization |
| **Development** | Python | 3.11+ | Development language |
| **GPU Computing** | CUDA | 13.0.2 | GPU acceleration |

### Development Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Unit testing |
| **black** | Code formatting |
| **flake8** | Linting |
| **isort** | Import sorting |
| **JupyterLab** | Interactive analysis |

---

## 11. AI Agent Guidelines

### Information Available to Agents

Each agent working on EASY has access to:

- ✓ This context document (EASY_PROJECT_CONTEXT.md)
- ✓ Project plan with timeline (docs/project_plan.md)
- ✓ Dataset strategy (docs/dataset_strategy.md)
- ✓ Model strategy (docs/model_strategy.md)
- ✓ Hardware integration plan (docs/hardware_integration_plan.md)
- ✓ Source code (src/ directory)
- ✓ Configuration files (configs/ directory)

### Agent Decision Authority

| Decision Type | Authority | Escalation |
|---------------|-----------|-----------|
| **Code fixes** | Full | None |
| **Small features** | Full | None if <100 lines |
| **New modules** | Full if aligned with roadmap | Document design rationale |
| **Dataset changes** | None without approval | Always escalate |
| **Model architecture** | Full for phase constraints | Justify deviations |
| **New dependencies** | Full if justified | Document in requirements |
| **Hardware integration** | Full if compatible | Test on RPi simulator |

### Mandatory Checks Before Commit

```
Before pushing ANY code:

[ ] Does it align with EASY goals?
[ ] Does it pass local testing?
[ ] Is it documented (docstrings, comments)?
[ ] Is the code formatted (black, isort)?
[ ] Does it pass flake8 linting?
[ ] Are new dependencies justified?
[ ] Does it fit the repository structure?
[ ] Is it compatible with Raspberry Pi constraints?
```

### Prohibited Actions

🚫 **Agents must NOT:**
- Modify dataset strategy without explicit approval
- Add classes beyond EASY-v0 specification
- Use proprietary libraries
- Implement advanced features skipping simpler alternatives
- Create new directory structures without justification
- Modify hardware assumptions
- Remove code without replacement
- Force merge conflicting changes

---

## 12. Success Metrics

### Phase 1 (Object Detection) Success Criteria

| Metric | Target | Validation |
|--------|--------|-----------|
| **mAP50** | ≥0.60 | COCO evaluation |
| **Inference FPS** | ≥15 FPS (RPi 5) | Real-time inference test |
| **Model Size** | ≤200 MB | YOLO export |
| **Class Accuracy** | ≥0.75 per class | Validation set |
| **Dataset Coverage** | 10,000+ images | EASY-v0 completion |
| **Documentation** | 100% modules documented | Auto-doc generation |

### Phase 2+ Criteria

To be defined during Phase 1 completion review.

---

## 13. Communication & Escalation

### Issue Resolution Path

```
Problem Identified
    ↓
Check this document & codebase
    ↓
Can solve independently? → YES → Implement & commit
    ↓ NO
Does it affect core architecture? → YES → Document objection + escalate
    ↓ NO
Propose minimal solution → Review → Implement
```

### Documentation of Decisions

All significant decisions must be recorded as:
```
**Decision:** [Brief title]
**Date:** [YYYY-MM-DD]
**Rationale:** [Why this choice]
**Alternatives Considered:** [What else was considered]
**Impact:** [Affected components]
```

---

## 14. Long-Term Vision (Post-Week 8)

### System Architecture

```
RGB Stream ──┐
             ├─→ [Object Detection] ──┐
FLIR Stream ─┤                        ├─→ [Tracking] ──→ [Environmental] 
             └──→ [Segmentation]  ────┤               Awareness
                                      └─→ [Fusion]
```

### Envisioned Capabilities

1. **Real-time Dual-Stream Processing**
   - Simultaneous RGB + FLIR analysis
   - Synchronized frame processing
   - Low-latency output

2. **Embedded Intelligence**
   - Run entirely on Raspberry Pi 5
   - No cloud dependency
   - Real-time inference (<100ms)

3. **Extensible Architecture**
   - Add new sensors (stereoscopic, LiDAR)
   - Extend class definitions
   - Custom model training pipeline

4. **Deployable System**
   - Docker containerization
   - Automated setup
   - Hardware abstraction layer

---

## 15. Document Maintenance

### Update Protocol

This document is a living artifact and must be updated when:

| Event | Action | Owner |
|-------|--------|-------|
| **Weekly checkpoint** | Review alignment, document changes | Project Lead |
| **Phase completion** | Update roadmap, finalize metrics | Team |
| **Major decision** | Add to decision log | Decision Maker |
| **Goal modification** | Update Section 2, justify rationale | Project Lead |
| **Technology change** | Update Section 10, document alternatives | Technical Lead |

### Version Control

- **Location:** `docs/EASY_PROJECT_CONTEXT.md`
- **History:** Git commit history
- **Format:** Markdown with semantic versioning
- **Accessibility:** Always available in repository

---

## Appendix A: Quick Reference

### Essential Commands

```bash
# Activate environment
source venv/bin/activate

# Setup project
bash scripts/setup_project.sh

# Prepare EASY-v0 dataset
bash scripts/prepare_easy_v0.sh

# Train baseline model
bash scripts/train_yolo_baseline.sh

# Run tests
pytest tests/ -v
```

### Key Configuration Files

- **Dataset:** `configs/dataset_easy_v0.yaml`
- **Training:** `configs/train_yolo.yaml`
- **Paths:** `configs/paths.yaml`

### Critical Paths

- **Source Code:** `/src/`
- **Data:** `/data/processed/EASY-v0/`
- **Models:** `/models/checkpoints/`
- **Outputs:** `/outputs/`

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| **EASY** | Environmental Awareness by the Sea and beYond |
| **RGB** | Red-Green-Blue color image data |
| **FLIR** | Forward-Looking Infrared thermal imaging |
| **mAP** | Mean Average Precision (detection metric) |
| **YOLO** | You Only Look Once (detection framework) |
| **RPi** | Raspberry Pi single-board computer |
| **COCO** | Common Objects in Context (annotation format) |
| **EASY-v0** | Initial unified dataset version |
| **YOLOv8n** | Nano version of YOLOv8 (lightweight) |

---

**Document Author:** Project Team  
**Last Review:** June 3, 2026  
**Next Review:** Week 4 checkpoint

---

*This document is the authoritative reference for EASY project development. All decisions, implementations, and modifications must be evaluated against the principles and constraints defined herein.*
