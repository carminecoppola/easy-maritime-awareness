# Hardware Integration Plan

## Overview

EASY system integrates Raspberry Pi with RGB and FLIR thermal cameras for autonomous maritime surveillance and object detection at the edge.

## Hardware Architecture

### Computing Platform

**Primary**: Raspberry Pi 4/5
- CPU: ARM Cortex-A72 (4 cores)
- RAM: 4GB / 8GB recommended
- Storage: 64GB microSD minimum
- USB: 4x USB 3.0
- Ethernet: Gigabit
- GPIO: 40 pins

**Alternative**: NVIDIA Jetson Nano
- More powerful GPU (128 CUDA cores)
- Better for real-time multimodal processing
- Higher power consumption

### RGB Camera

**Option 1**: Raspberry Pi Camera Module v2
- Resolution: 8MP (3280x2464)
- Sensor: Sony IMX219
- Interface: CSI ribbon
- Cost: ~$25

**Option 2**: USB Camera with zoom
- Resolution: 4K-capable
- Better for long-range detection
- Easier to mount

### Thermal Camera (FLIR)

**Option 1**: FLIR Lepton 3.5
- Resolution: 160x120 (radiometric)
- Price: ~$100-150
- Interface: I2C + SPI
- Integration: Breakout board available

**Option 2**: FLIR Boson
- Higher resolution: 320x256
- Better thermal sensitivity
- Price: ~$500+
- Professional-grade

### Power Supply

- **PSU**: 5V/3A USB-C for RPi 4
- **Battery**: For mobile deployment
  - Option: 20000mAh power bank
  - Runtime: 8-10 hours
  - Or: LiPo 5V regulator + solar panel

### Enclosure & Mounting

- IP67-rated enclosure (weatherproof)
- Camera mounts and gimbals
- Cable management
- Thermal ventilation holes

## Setup & Installation

### Week 5: Raspberry Pi Setup

#### 5.1 OS Installation

```bash
# Download Raspberry Pi OS Lite (headless recommended)
# Use Raspberry Pi Imager to flash microSD

# First boot
sudo raspi-config
# - Enable SSH
# - Enable I2C / SPI
# - Set GPU memory to 256MB
# - Set hostname
```

#### 5.2 System Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    git python3-pip python3-dev \
    build-essential libatlas-base-dev \
    libjasper-dev libtiff5 libjasper1 \
    libharfbuzz0b libwebp6 libtiff5 \
    libhyperbas3

# Install Python packages
pip3 install --upgrade pip
pip3 install numpy opencv-python pillow tqdm
```

#### 5.3 YOLO Runtime Installation

```bash
# Install PyTorch (CPU or edge-optimized)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install ultralytics
pip3 install ultralytics

# Or use ONNX Runtime (lower latency)
pip3 install onnxruntime
```

### Week 5: RGB Camera Setup

#### 5.4 RGB Camera Configuration

```bash
# Enable camera in device tree
sudo raspi-config
# Interfacing Options → Camera → Enable

# Test camera
raspistill -o test.jpg
python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print(frame.shape)"
```

#### 5.5 RGB Data Collection Script

```python
#!/usr/bin/env python3
"""Collect RGB video from RPi camera"""

import cv2
import time
from pathlib import Path

output_dir = Path("data/raw/easy_acquisition/rgb")
output_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(
    str(output_dir / f"video_{int(time.time())}.mp4"),
    fourcc, 30.0, (640, 480)
)

print("Recording RGB video (press Ctrl+C to stop)...")
try:
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
except KeyboardInterrupt:
    pass
finally:
    cap.release()
    out.release()
    print("Video saved")
```

### Week 6: FLIR Integration

#### 6.1 FLIR Lepton Setup (if using)

```bash
# Install Lepton dependencies
pip3 install adafruit-circuitpython-cci

# Enable I2C/SPI
sudo raspi-config
# Interfacing Options → I2C → Enable
# Interfacing Options → SPI → Enable

# Test FLIR connection
python3 scripts/test_flir_connection.py
```

#### 6.2 FLIR Data Collection

```python
#!/usr/bin/env python3
"""Collect thermal data from FLIR camera"""

import numpy as np
import cv2
from pathlib import Path

output_dir = Path("data/raw/easy_acquisition/thermal")
output_dir.mkdir(parents=True, exist_ok=True)

# Initialize FLIR camera (implementation depends on hardware)
# thermal_camera = FLIRLepton()

# Collect thermal frames
for i in range(100):
    # frame = thermal_camera.get_frame()  # Returns (160, 120)
    # Normalize to 0-255 for visualization
    # frame_uint8 = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    # cv2.imwrite(f"{output_dir}/thermal_{i:04d}.png", frame_uint8)
    pass
```

## Real-Time Inference

### Week 5: RGB Inference Script

```python
#!/usr/bin/env python3
"""Real-time RGB inference on Raspberry Pi"""

from ultralytics import YOLO
import cv2
import time

# Load model (quantized for RPi)
model = YOLO("models/exported/yolov8n.tflite")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 416)

fps_start = time.time()
frame_count = 0

print("Starting real-time inference...")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Inference
    results = model(frame, conf=0.5)
    
    # Visualize
    annotated_frame = results[0].plot()
    
    # FPS calculation
    frame_count += 1
    elapsed = time.time() - fps_start
    if elapsed > 1:
        fps = frame_count / elapsed
        print(f"FPS: {fps:.1f}")
        frame_count = 0
        fps_start = time.time()
    
    cv2.imshow("EASY Detection", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Week 6: Multimodal Inference

```python
#!/usr/bin/env python3
"""Real-time RGB + Thermal inference"""

from ultralytics import YOLO
import cv2
import numpy as np
import time

# Load multimodal model
model = YOLO("models/exported/yolov8n_multimodal.tflite")

cap_rgb = cv2.VideoCapture(0)
# thermal_camera = FLIRLepton()

while True:
    ret, frame_rgb = cap_rgb.read()
    # frame_thermal = thermal_camera.get_frame()
    
    if not ret:
        break
    
    # Resize frames
    frame_rgb = cv2.resize(frame_rgb, (416, 416))
    # frame_thermal = cv2.resize(frame_thermal, (416, 416))
    # frame_thermal = cv2.normalize(frame_thermal, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    # Stack inputs
    # dual_input = np.concatenate([frame_rgb, np.stack([frame_thermal]*3, -1)], axis=-1)
    
    # Inference (multimodal model)
    # results = model(dual_input, conf=0.5)
    
    # Visualize
    # annotated_frame = results[0].plot()
    # cv2.imshow("EASY Multimodal Detection", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

## Model Export for Edge Deployment

### Model Optimization

```python
from ultralytics import YOLO

# Load trained model
model = YOLO("models/checkpoints/yolov8m_best.pt")

# Export to TensorFlow Lite (for RPi)
model.export(format="tflite", imgsz=416, half=True)

# Export to ONNX (general purpose)
model.export(format="onnx", imgsz=416, half=True)

# Export to NCNN (mobile optimized)
model.export(format="ncnn", imgsz=416)
```

### Quantization for RPi

```python
from ultralytics import YOLO
import torch

model = YOLO("models/checkpoints/yolov8n_best.pt")

# INT8 Quantization
model.model = torch.quantization.quantize_dynamic(
    model.model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Export quantized model
model.export(format="tflite", int8=True)
```

## Performance Benchmarking

### Benchmarking Script

```python
import cv2
import time
from ultralytics import YOLO

model = YOLO("models/exported/yolov8n.tflite")

# Load test image
frame = cv2.imread("test_image.jpg")

# Warmup
for _ in range(5):
    model(frame)

# Benchmark
times = []
for _ in range(100):
    start = time.time()
    results = model(frame)
    times.append(time.time() - start)

print(f"Mean latency: {np.mean(times)*1000:.1f} ms")
print(f"Std latency: {np.std(times)*1000:.1f} ms")
print(f"Min latency: {np.min(times)*1000:.1f} ms")
print(f"Max latency: {np.max(times)*1000:.1f} ms")
print(f"FPS: {1/np.mean(times):.1f}")
```

## System Monitoring

### Resource Monitor Script

```bash
#!/bin/bash
# Monitor CPU, GPU, memory, temperature

while true; do
    clear
    echo "=== EASY System Monitor ==="
    echo "CPU Temp: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000}')°C"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"
    echo "RAM Usage: $(free -h | awk '/^Mem:/{print $3}')"
    echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
    sleep 2
done
```

## Deployment Checklist

- [ ] Raspberry Pi OS installed and configured
- [ ] SSH access enabled and secured
- [ ] Python 3.9+ installed with virtual environment
- [ ] PyTorch and YOLO runtime installed
- [ ] RGB camera tested and working
- [ ] FLIR camera tested and working
- [ ] Models exported and optimized
- [ ] Real-time inference scripts tested
- [ ] Power supply verified for 8+ hours
- [ ] Enclosure weatherproofed
- [ ] Network connectivity configured (WiFi/Ethernet)
- [ ] Logging and monitoring setup
- [ ] Backup system configured

## Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check CSI ribbon connection
   - Run `vcgencmd get_camera`
   - Re-enable in raspi-config

2. **Low FPS**
   - Reduce inference resolution
   - Use nano model variant
   - Enable quantization
   - Disable unnecessary post-processing

3. **Memory errors**
   - Reduce batch processing
   - Use model streaming
   - Enable swap (performance trade-off)

4. **Thermal camera connection**
   - Verify I2C/SPI enabled
   - Check pull-up resistors
   - Test with i2cdetect

## Future Enhancements

1. **LoRaWAN Integration**: Send detections to cloud
2. **Edge Training**: Fine-tune model on RPi
3. **Redundancy**: Dual RPi setup for failover
4. **Analytics Dashboard**: Real-time monitoring UI
5. **Cloud Sync**: Periodic model updates from cloud
