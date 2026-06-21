# EASY Training And Experiment Results

## Official Baseline Result

Official baseline:

`EASY-v1-rgb3-buoy-rebalanced`

Weights:

`outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt`

## EASY-v1 Test Metrics

| Metric | Value |
| --- | ---: |
| Precision | 0.91463 |
| Recall | 0.91807 |
| mAP50 | 0.94207 |
| mAP50-95 | 0.70694 |

Per class:

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| boat | 0.92449 | 0.87524 | 0.93927 | 0.67771 |
| ship | 0.82078 | 0.87897 | 0.89195 | 0.61534 |
| buoy | 0.99862 | 1.00000 | 0.99500 | 0.82777 |

## Main Discovery

The original EASY failure was mostly a dataset-composition problem, not a YOLOv8n capacity problem.

Evidence:

- EASY-v0 had severe buoy collapse.
- EASY-v1 changed dataset composition and recovered buoy performance.
- Architecture and core training setup stayed effectively unchanged.

## Buoy Result

EASY-v1 fixed the buoy failure.

Boat/buoy confusion on EASY-v1 test:

| Error Type | Count |
| --- | ---: |
| buoy -> boat | 0 / 373 |
| boat -> buoy | 0 / 529 |

Conclusion:

The buoy problem is solved in the official baseline.

## Remaining Weakness

The remaining weakness is boat detection, especially:

- low-contrast boats
- dark boats
- medium slender boats
- partially visible boats
- boat-vs-ship boundary cases

However, later experiments showed that aggressive dataset/split iteration did not produce a better official baseline.

## EASY-v2 Result

EASY-v2 removed sequence/source-group leakage and was methodologically cleaner than EASY-v1.

It failed metric-wise because buoy collapsed on test.

| Metric | EASY-v1 | EASY-v2 | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.91463 | 0.94115 | +0.02652 |
| Recall | 0.91807 | 0.60069 | -0.31738 |
| mAP50 | 0.94207 | 0.75655 | -0.18552 |
| mAP50-95 | 0.70694 | 0.47432 | -0.23262 |

Buoy:

| Metric | EASY-v1 | EASY-v2 |
| --- | ---: | ---: |
| Recall | 1.00000 | 0.00000 |
| mAP50 | 0.99500 | 0.38281 |

Decision:

EASY-v2 is not a baseline.

## EASY-v2.1 Result

EASY-v2.1 added buoy-aware split constraints and passed the pre-training gate.

It still failed on test.

| Metric | EASY-v1 | EASY-v2 | EASY-v2.1 |
| --- | ---: | ---: | ---: |
| Precision | 0.91463 | 0.94115 | 0.95614 |
| Recall | 0.91807 | 0.60069 | 0.50132 |
| mAP50 | 0.94207 | 0.75655 | 0.52923 |
| mAP50-95 | 0.70694 | 0.47432 | 0.36110 |

EASY-v2.1 per class:

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| boat | 0.93942 | 0.60517 | 0.63552 | 0.43812 |
| ship | 0.92898 | 0.89879 | 0.95216 | 0.64519 |
| buoy | 1.00000 | 0.00000 | 0.00000 | 0.00000 |

Decision:

EASY-v2.1 is not a baseline.

## Final Scientific Conclusion

EASY-v1 remains the final official baseline.

EASY-v2 and EASY-v2.1 showed that stricter sequence-safe evaluation is scientifically valuable, but the currently available internal data does not support robust generalization under that stricter benchmark.

Dataset iteration stops here.

## Canonical Reports

The only active reports are:

- `outputs/reports/easy_dataset_iteration_closure.md`
- `outputs/reports/easy_v1_test_evaluation.md`
- `outputs/reports/easy_v1_buoy_rebalanced_report.md`
- `outputs/reports/repository_final_cleanup_report.md`

All intermediate reports are archived under:

`archive/cleanup_20260620_repo_reset/reports/`
