# Deployment Notes

> **Historical.** This documents how the leakage-affected EASY-v1 weights
> were exported. The export *mechanism* (Ultralytics ONNX export, class
> mapping, letterbox preprocessing) is still how the current sequence-safe +
> ABOships models are exported — only the source `.pt` path changes. For
> which model is actually current, see `docs/TRAINING_AND_EXPERIMENT_RESULTS.md`
> and `outputs/reports/easy_v3_results.md`.

## Export

- Source model: `models/easy_v1_best_rgb.pt`
- Exported ONNX: `models/easy_v1_best_rgb.onnx`
- Export command equivalent: `python -m ultralytics export model=models/easy_v1_best_rgb.pt format=onnx imgsz=640 opset=12 simplify=True`
- Class mapping: `0=boat`, `1=ship`, `2=buoy`.
- Preprocessing: RGB input with Ultralytics letterbox for imgsz `640`.
- Raspberry follow-up: validate latency, RAM, and prediction parity with representative maritime frames.

