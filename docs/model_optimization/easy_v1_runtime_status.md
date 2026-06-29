# EASY-v1 Runtime Status

Generated: `2026-06-26T14:35:09.183472Z`

## Summary

| Requirement | Status | Detail |
| --- | --- | --- |
| Python >= 3.9 | PASS | `3.11.7` via `archive/easy_v1_legacy_backup/root/venv/bin/python` |
| Module `onnx` | PASS | 1.22.0 |
| Module `torch` | PASS | 2.5.1+cu121 |
| Module `ultralytics` | PASS | 8.4.60 |
| CUDA | FAIL | torch installed but CUDA not available |
| Baseline weights | PASS | `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt` |
| Pretrained weights `models/pretrained/yolov8s.pt` | PASS | size `21.54 MB` |

## Blockers

- CUDA-capable runtime not available

Machine-readable status: `outputs/reports/phase1_artifacts/easy_v1_runtime_status.json`.

