# EASY-v1 Experiment Comparison

> **Historical / superseded.** This documents the EASY-v1 phase-1 run only (leakage-affected, mAP50 0.94207 not trustworthy). For current results see `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` and `outputs/reports/easy_v3_results.md`.

Generated from fresh Phase 1 evaluations.

## Val

| Run name | Model | imgsz | epochs | precision | recall | mAP50 | mAP50-95 | boat precision/recall/mAP50 | ship precision/recall/mAP50 | buoy precision/recall/mAP50 | model size | inference speed | note qualitative |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| easy_v1_rgb_phase1_baseline | YOLOv8n | 640 | 50 | 0.88301 | 0.77393 | 0.77884 | 0.56233 | 0.81485/0.43096/0.48145 | 0.83588/0.89084/0.86007 | 0.99831/1.00000/0.99500 | 5.94 MB | 0.90 ms | Historical baseline retrained metrics consolidated with fresh Phase 1 eval. |
| easy_v1_rgb_phase1_exp_a_yolov8s_640 | yolov8s | 640 | 50 | 0.86789 | 0.77915 | 0.80574 | 0.58259 | 0.75952/0.48233/0.54222 | 0.84644/0.85511/0.88001 | 0.99772/1.00000/0.99500 | 21.45 MB | 1.70 ms | Baseline-style augmentation close to the official YOLOv8n run. |
| easy_v1_rgb_phase1_exp_b_yolov8s_960 | yolov8s | 960 | 50 | 0.90378 | 0.76328 | 0.79364 | 0.59019 | 0.86168/0.39099/0.50173 | 0.85190/0.89886/0.88419 | 0.99774/1.00000/0.99500 | 21.49 MB | 3.47 ms | Higher resolution for small-object sensitivity, especially buoy. |
| easy_v1_rgb_phase1_exp_c_yolov8s_640_maritime_aug | yolov8s | 640 | 50 | 0.92307 | 0.74168 | 0.77614 | 0.58246 | 0.89502/0.42808/0.49288 | 0.87507/0.79696/0.84054 | 0.99913/1.00000/0.99500 | 21.45 MB | 1.70 ms | Controlled maritime augmentation with reduced aggressive transforms. |

## Test

| Run name | Model | imgsz | epochs | precision | recall | mAP50 | mAP50-95 | boat precision/recall/mAP50 | ship precision/recall/mAP50 | buoy precision/recall/mAP50 | model size | inference speed | note qualitative |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| easy_v1_rgb_phase1_baseline | YOLOv8n | 640 | 50 | 0.91463 | 0.91807 | 0.94207 | 0.70694 | 0.92449/0.87524/0.93927 | 0.82078/0.87897/0.89195 | 0.99862/1.00000/0.99500 | 5.94 MB | 0.83 ms | Historical baseline retrained metrics consolidated with fresh Phase 1 eval. |
| easy_v1_rgb_phase1_exp_a_yolov8s_640 | yolov8s | 640 | 50 | 0.93348 | 0.92777 | 0.94820 | 0.71848 | 0.91267/0.94827/0.96512 | 0.88818/0.83504/0.88448 | 0.99960/1.00000/0.99500 | 21.45 MB | 1.69 ms | Baseline-style augmentation close to the official YOLOv8n run. |
| easy_v1_rgb_phase1_exp_b_yolov8s_960 | yolov8s | 960 | 50 | 0.92915 | 0.91558 | 0.93238 | 0.72514 | 0.94646/0.89225/0.93815 | 0.84216/0.85448/0.86400 | 0.99883/1.00000/0.99500 | 21.49 MB | 3.47 ms | Higher resolution for small-object sensitivity, especially buoy. |
| easy_v1_rgb_phase1_exp_c_yolov8s_640_maritime_aug | yolov8s | 640 | 50 | 0.93012 | 0.90225 | 0.91745 | 0.70723 | 0.94818/0.86476/0.91890 | 0.84328/0.84200/0.83846 | 0.99891/1.00000/0.99500 | 21.45 MB | 1.70 ms | Controlled maritime augmentation with reduced aggressive transforms. |

