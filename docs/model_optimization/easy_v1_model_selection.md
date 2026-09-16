# EASY-v1 Model Selection

> **Historical / superseded.** This documents the EASY-v1 phase-1 run only (leakage-affected, mAP50 0.94207 not trustworthy). For current results see `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` and `outputs/reports/easy_v3_results.md`.

## Winner

- Run: `easy_v1_rgb_phase1_baseline`
- Source weights: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt`
- Copied model: `models/easy_v1_best_rgb.pt`

## Ranking

| Rank | Run | Buoy recall | Recall spread | mAP50 | mAP50-95 | Model size MB |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | easy_v1_rgb_phase1_baseline | 1.00000 | 0.12476 | 0.94207 | 0.70694 | 5.94 |
| 2 | easy_v1_rgb_phase1_exp_b_yolov8s_960 | 1.00000 | 0.14552 | 0.93238 | 0.72514 | 21.49 |
| 3 | easy_v1_rgb_phase1_exp_c_yolov8s_640_maritime_aug | 1.00000 | 0.15800 | 0.91745 | 0.70723 | 21.45 |
| 4 | easy_v1_rgb_phase1_exp_a_yolov8s_640 | 1.00000 | 0.16496 | 0.94820 | 0.71848 | 21.45 |

## Decision Rationale

Selection order was: buoy recall, class stability, mAP50, mAP50-95, model size, Raspberry deployability.

