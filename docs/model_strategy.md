# Model Strategy

## Overview

EASY uses YOLO (You Only Look Once) models for real-time maritime object detection, with a clear path to edge deployment on Raspberry Pi with multimodal capabilities.

## Model Selection

### Primary: YOLOv8

**Why YOLOv8?**
- State-of-the-art real-time detection
- Multiple size variants (nano, small, medium, large, xlarge)
- Excellent community support and documentation
- Native ONNX and TensorFlow Lite export
- Strong performance on edge devices

**Variants**:
- **YOLOv8n** (nano): ~3M params - for RPi edge deployment
- **YOLOv8s** (small): ~11M params - balanced speed/accuracy
- **YOLOv8m** (medium): ~26M params - **baseline**
- **YOLOv8l** (large): ~43M params - best accuracy
- **YOLOv8x** (xlarge): ~71M params - maximum accuracy

### Baseline: YOLOv8-m

- **Model Size**: 26M parameters
- **Input Resolution**: 640x640 (configurable)
- **Inference Speed**: ~25 FPS on V100 GPU
- **Pretrained Weights**: COCO-pretrained
- **Strategy**: Transfer learning from general object detection

## Training Strategy

### Phase 1: Baseline (Week 3)

```yaml
Architecture: YOLOv8-m
Epochs: 100
Batch Size: 32
Learning Rate: 0.01 (with cosine annealing)
Warmup Epochs: 3
Device: GPU (single V100 or equivalent)
```

**Target Metrics**:
- mAP50: >60%
- mAP50-95: >40%
- Training Time: ~12-24 hours

### Phase 2: Fine-tuning (Week 7-8)

```yaml
Fine-tune from: YOLOv8-m (baseline)
Epochs: 50
Batch Size: 64
Learning Rate: 0.001 (lower)
Frozen Layers: First 10 layers
```

**Improvements**:
- Better EASY-v0 specific features
- Fine-grained class distinctions
- Maritime context specialization

## Data Preparation

### Preprocessing

1. **Image Normalization**
   - ImageNet statistics or dataset-specific
   - Resize with aspect ratio preservation
   - Padding to 640x640

2. **Label Preparation**
   - YOLO format conversion (completed)
   - Class ID consistency check
   - Coordinate normalization validation

### Augmentation Configuration

```yaml
HSV-H: ±0.015
HSV-S: ±0.7
HSV-V: ±0.4
Degrees: 0.0 (no rotation - maritime alignment)
Translate: ±0.1
Scale: ±0.5
Flip-LR: 50%
Mosaic: Enabled
```

## Loss Function

### Components

```
Total Loss = λ_box * L_box + λ_cls * L_cls + λ_obj * L_obj
```

- **L_box**: Localization loss (CIoU)
- **L_cls**: Classification loss (BCE)
- **L_obj**: Objectness loss (BCE)

### Weights

```yaml
λ_box: 7.5
λ_cls: 0.5
λ_obj: 1.0
```

## Inference Pipeline

### Standard Inference

1. **Preprocessing**: Resize & normalize image
2. **Forward Pass**: Model inference
3. **Post-processing**: NMS (Confidence: 0.5, IoU: 0.6)
4. **Output**: Bounding boxes with confidence scores

### Metrics

- **Inference Time**: Per-image latency
- **Throughput**: Images per second
- **Memory Usage**: GPU/CPU peak

## Edge Deployment

### Model Optimization for RPi

1. **Quantization**
   - FP32 → FP16 or INT8
   - ~50% model size reduction
   - Minimal accuracy loss

2. **Pruning**
   - Remove low-importance weights
   - Target 30-40% sparsity
   - Fine-tune after pruning

3. **Export Formats**
   - PyTorch: `.pt` (reference)
   - ONNX: `.onnx` (general inference)
   - TensorFlow Lite: `.tflite` (RPi native)
   - NCNN: `.bin`, `.param` (mobile optimized)

### Target Performance (RPi 4)

- **Model**: YOLOv8n (nano variant)
- **Resolution**: 416x416 (reduced)
- **Inference Speed**: >5 FPS
- **Memory**: <200MB RAM
- **Latency**: <200ms per frame

## Multimodal Strategy

### RGB + Thermal Fusion

1. **Input Branch 1**: RGB camera (640x480)
2. **Input Branch 2**: FLIR thermal (640x480)
3. **Fusion Layer**: Early fusion in backbone
4. **Output**: Unified detections

### Architecture Modifications

```
RGB Stream → Feature Extraction → 
                                    ├─ Fusion Layer → Detection Head
FLIR Stream → Feature Extraction →
```

### Benefits

- Thermal detects heat signatures (nighttime)
- RGB provides color context
- Complementary information reduces false positives
- Robust in varying lighting conditions

## Evaluation Metrics

### Primary Metrics

- **mAP50**: Mean Average Precision at IoU=0.5
- **mAP50-95**: Mean AP averaged over IoU thresholds
- **Precision**: True Positives / (TP + FP)
- **Recall**: True Positives / (TP + FN)

### Per-Class Analysis

- Per-class mAP
- Class-specific precision/recall
- Confusion matrix

### Runtime Metrics

- FPS (frames per second)
- Latency (milliseconds per frame)
- GPU memory usage
- Throughput

## Hyperparameter Tuning

### Grid Search Space

```yaml
Learning Rate: [0.001, 0.005, 0.01]
Batch Size: [16, 32, 64]
Weight Decay: [0.0, 0.0005, 0.001]
Momentum: [0.9, 0.937]
```

### Early Stopping

- Monitor validation mAP
- Stop if no improvement for 20 epochs
- Save best checkpoint

## Model Checkpointing

### Saved Artifacts

- **Best Model**: Highest validation mAP
- **Last Model**: Final epoch
- **Backup**: Every 10 epochs

### Checkpoint Information

```yaml
Epoch: 100
mAP50: 0.65
mAP50-95: 0.45
Precision: 0.72
Recall: 0.58
Training Time: 18.5 hours
```

## Future Improvements

1. **Architecture Exploration**
   - YOLOv9 when released
   - Vision Transformers (ViT)
   - Hybrid architectures

2. **Advanced Training**
   - Multi-task learning (detection + segmentation)
   - Self-supervised pre-training
   - Meta-learning for few-shot adaptation

3. **Deployment**
   - Autonomous system integration
   - Real-time statistics dashboard
   - On-device model updates
