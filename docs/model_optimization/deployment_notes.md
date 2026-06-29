# Deployment Notes

## Export

- Source model: `models/easy_v1_best_rgb.pt`
- Exported ONNX: `models/easy_v1_best_rgb.onnx`
- Export command equivalent: `python -m ultralytics export model=models/easy_v1_best_rgb.pt format=onnx imgsz=640 opset=12 simplify=True`
- Class mapping: `0=boat`, `1=ship`, `2=buoy`.
- Preprocessing: RGB input with Ultralytics letterbox for imgsz `640`.
- Raspberry follow-up: validate latency, RAM, and prediction parity with representative maritime frames.

