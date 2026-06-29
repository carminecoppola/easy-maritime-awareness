# EASY-v1 Baseline Full Evaluation

Generated from fresh Phase 1 evaluation artifacts.

## Baseline Reference

- Run: `easy_v1_rgb_phase1_baseline`
- Weights: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt`
- Validation artifacts: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_val`
- Test artifacts: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_test`

## Validation Metrics

| Metric | Value |
| --- | ---: |
| Precision | 0.88301 |
| Recall | 0.77393 |
| mAP50 | 0.77884 |
| mAP50-95 | 0.56233 |
| F1 | 0.82488 |

| Class | Precision | Recall | mAP50 | mAP50-95 | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| boat | 0.81485 | 0.43096 | 0.48145 | 0.27739 | 0.56376 |
| ship | 0.83588 | 0.89084 | 0.86007 | 0.57911 | 0.86249 |
| buoy | 0.99831 | 1.00000 | 0.99500 | 0.83051 | 0.99915 |

## Test Metrics

| Metric | Value |
| --- | ---: |
| Precision | 0.91463 |
| Recall | 0.91807 |
| mAP50 | 0.94207 |
| mAP50-95 | 0.70694 |
| F1 | 0.91635 |

| Class | Precision | Recall | mAP50 | mAP50-95 | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| boat | 0.92449 | 0.87524 | 0.93927 | 0.67771 | 0.89919 |
| ship | 0.82078 | 0.87897 | 0.89195 | 0.61534 | 0.84888 |
| buoy | 0.99862 | 1.00000 | 0.99500 | 0.82777 | 0.99931 |

## Confusion Matrices And Predictions

- Validation confusion matrix: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_val/confusion_matrix.png`
- Test confusion matrix: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_test/confusion_matrix.png`
- Validation predictions: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_val/predictions.json`
- Test predictions: `outputs/experiments/easy_v1_rgb_phase1/easy_v1_rgb_phase1_baseline_test/predictions.json`
