# EASY-v1 Test Evaluation

## Weights Used

- best weights: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt`
- last weights: `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/last.pt`

This evaluation uses `best.pt`.

## Test Evaluation

Dataset:

- `data/processed/EASY-v1-rgb3-buoy-rebalanced/images/test`

Primary metric artifact:

- `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced_test/metrics_summary.json`

Global metrics:

| Metric | Test |
| --- | ---: |
| Precision | 0.91463 |
| Recall | 0.91807 |
| mAP50 | 0.94207 |
| mAP50-95 | 0.70694 |

Per-class metrics:

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| boat | 0.92449 | 0.87524 | 0.93927 | 0.67771 |
| ship | 0.82078 | 0.87897 | 0.89195 | 0.61534 |
| buoy | 0.99862 | 1.00000 | 0.99500 | 0.82777 |

## Confusion Analysis

Ultralytics test artifacts were saved under:

- confusion matrix: `runs/detect/outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced_test-2/confusion_matrix.png`
- normalized confusion matrix: `runs/detect/outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced_test-2/confusion_matrix_normalized.png`
- predictions: `runs/detect/outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced_test-2/predictions.json`

Boat<->buoy confusion quantified with greedy IoU `>= 0.5` matching against test ground truth:

| Error Type | Count |
| --- | ---: |
| buoy -> boat | 0 / 373 |
| boat -> buoy | 0 / 529 |

## Validation vs Test

Global comparison:

| Metric | Validation | Test | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.88301 | 0.91463 | +0.03161 |
| Recall | 0.77393 | 0.91807 | +0.14414 |
| mAP50 | 0.77884 | 0.94207 | +0.16323 |
| mAP50-95 | 0.56233 | 0.70694 | +0.14461 |

Per-class comparison:

| Class | Metric | Validation | Test | Delta |
| --- | --- | ---: | ---: | ---: |
| boat | Precision | 0.81485 | 0.92449 | +0.10964 |
| boat | Recall | 0.43096 | 0.87524 | +0.44427 |
| boat | mAP50 | 0.48145 | 0.93927 | +0.45782 |
| boat | mAP50-95 | 0.27739 | 0.67771 | +0.40032 |
| ship | Precision | 0.83588 | 0.82078 | -0.01511 |
| ship | Recall | 0.89084 | 0.87897 | -0.01186 |
| ship | mAP50 | 0.86007 | 0.89195 | +0.03187 |
| ship | mAP50-95 | 0.57911 | 0.61534 | +0.03623 |
| buoy | Precision | 0.99831 | 0.99862 | +0.00031 |
| buoy | Recall | 1.00000 | 1.00000 | +0.00000 |
| buoy | mAP50 | 0.99500 | 0.99500 | +0.00000 |
| buoy | mAP50-95 | 0.83051 | 0.82777 | -0.00274 |

## Decision

### Q1

Did buoy performance remain stable?

YES.

Buoy metrics remain effectively unchanged from validation to test:

- Precision: `0.99831 -> 0.99862`
- Recall: `1.00000 -> 1.00000`
- mAP50: `0.99500 -> 0.99500`
- mAP50-95: `0.83051 -> 0.82777`

### Q2

Did boat<->buoy confusion remain low?

YES.

Using IoU `>= 0.5` matching on the test set:

- buoy -> boat: `0 / 373`
- boat -> buoy: `0 / 529`

### Q3

Does the evidence support the dataset hypothesis?

YES.

The buoy gains observed on validation generalize to the test split without retraining or model-side changes. That strongly supports the conclusion that dataset composition and buoy representation were the main drivers of the original buoy failure.
