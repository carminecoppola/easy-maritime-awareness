# Model card — EASY maritime object detectors

## Released files

| File | Role | SHA-256 |
| --- | --- | --- |
| `easy_v3_aboships_640.onnx` | **Current model**, used by the dashboard | `7b7caf0d…2b87c9` |
| `easy_v1_best_rgb.onnx`, `easy_v1_best_rgb.pt` | Legacy EASY-v1 baseline, **leakage-affected, historical only** | see `checksums.sha256` |

Verify a download with `shasum -a 256 -c models/checksums.sha256`. The dashboard
repository ships a byte-identical copy of `easy_v3_aboships_640.onnx` in
`runtime/models/`.

## `easy_v3_aboships_640.onnx`

| | |
| --- | --- |
| Architecture | YOLOv8n (Ultralytics 8.4.60), single-stage detector |
| Task | Object detection, RGB images |
| Classes | `0 boat`, `1 ship`, `2 buoy` |
| Input | `images`, float32, `[1, 3, 640, 640]`, RGB in [0, 1], letterboxed (padding value 114) |
| Output | `output0`, `[1, 7, 8400]`: 4 box values (cx, cy, w, h in input pixels) + 3 class scores per anchor; no built-in NMS |
| Export | ONNX opset 12, simplified, static batch 1, exported on 2026-09-10 |
| Training data | SMD + SeaShips + ABOships, split with `scripts/dataset/build_sequence_safe_split.py` (no sequence shared between sets) |
| Training recipe | 50 epochs from COCO-pretrained YOLOv8n, seed 42, patience 20 (`scripts/validation/train_sequence_safe_candidate.py`) |
| Deployed on | Raspberry Pi 4, ONNX Runtime CPU, ≈ 0.6 s model time per frame |

### Reference decoding

Confidence threshold 0.25, class-wise NMS with IoU 0.45 (the values used by the
dashboard, `inference_image.py`). Boxes map back to the image by removing the
letterbox padding and dividing by the scale ratio.

### Measured performance

Internal sequence-safe test set:

| Precision | Recall | mAP50 | mAP50-95 | Buoy recall |
| ---: | ---: | ---: | ---: | ---: |
| 0.699 | 0.592 | 0.627 | 0.314 | 0.485 |

External benchmark MODD2 (open water, never seen in training), class-agnostic
object-level recall at IoU 0.3: **3.87%** for the best EASY-v3 model (the 960 px
variant; a MODD2 figure for the 640 px model was not recorded). On 124 non-maritime
images, 16.9% of the EASY-v1 detections were false positives (always `ship`); this
scan has not been repeated on the v3 models.

Full methodology: [`outputs/reports/easy_v3_results.md`](../outputs/reports/easy_v3_results.md).

### Intended use and limitations

**Intended use:** assisting data collection and research on the EASY edge node, on
RGB images of the kind found in SMD, SeaShips and ABOships (coastal and port scenes).

**Not intended for** navigation, collision avoidance or any safety-critical decision.
It is **not validated for open water**: small and distant obstacles are mostly missed,
and non-maritime content can trigger false `ship` detections. Thermal images are not
supported.

### Licence

The EASY code is BSD-3-Clause. These weights were produced with Ultralytics YOLOv8,
whose terms (AGPL-3.0, or an Ultralytics enterprise licence) apply to models trained
and exported with it; the ONNX metadata says so. They were trained on third-party
datasets with their own terms (ABOships is CC BY 4.0 and requires attribution). See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) before redistributing or using
the weights commercially.
