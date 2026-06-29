# EASY Dataset Iteration Closure Report

## 1. Official Baseline

`EASY-v1-rgb3-buoy-rebalanced` remains the official EASY baseline.

Dataset path:

`data/processed/EASY-v1-rgb3-buoy-rebalanced`

### EASY-v1 Global Metrics

| Metric | Value |
| --- | ---: |
| Precision | 0.91463 |
| Recall | 0.91807 |
| mAP50 | 0.94207 |
| mAP50-95 | 0.70694 |

### EASY-v1 Per-Class Metrics

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| boat | 0.92449 | 0.87524 | 0.93927 | 0.67771 |
| ship | 0.82078 | 0.87897 | 0.89195 | 0.61534 |
| buoy | 0.99862 | 1.00000 | 0.99500 | 0.82777 |

## 2. EASY-v2 Findings

EASY-v2 removed sequence/source-group leakage and was methodologically cleaner than EASY-v1.

However, EASY-v2 failed as a replacement baseline because test performance collapsed, primarily due to buoy failure.

### EASY-v2 Test Summary

| Metric | EASY-v1 | EASY-v2 | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.91463 | 0.94115 | +0.02652 |
| Recall | 0.91807 | 0.60069 | -0.31738 |
| mAP50 | 0.94207 | 0.75655 | -0.18552 |
| mAP50-95 | 0.70694 | 0.47432 | -0.23262 |

### EASY-v2 Buoy Failure

| Metric | EASY-v1 Buoy | EASY-v2 Buoy | Delta |
| --- | ---: | ---: | ---: |
| Precision | 0.99862 | 1.00000 | +0.00138 |
| Recall | 1.00000 | 0.00000 | -1.00000 |
| mAP50 | 0.99500 | 0.38281 | -0.61219 |
| mAP50-95 | 0.82777 | 0.15988 | -0.66789 |

EASY-v2 showed that removing leakage made evaluation stricter, but the candidate split exposed insufficient robust buoy generalization.

## 3. EASY-v2.1 Findings

EASY-v2.1 added buoy-aware split constraints while preserving sequence safety and leakage-free evaluation.

The dataset passed the pre-training gate:

- audit PASS
- zero source-group leakage
- all classes present in train/val/test
- buoy present in train/val/test
- train contained multiple buoy scale regimes

Despite that, EASY-v2.1 still failed as a replacement baseline.

### EASY-v2.1 Test Summary

| Metric | EASY-v1 | EASY-v2 | EASY-v2.1 |
| --- | ---: | ---: | ---: |
| Precision | 0.91463 | 0.94115 | 0.95614 |
| Recall | 0.91807 | 0.60069 | 0.50132 |
| mAP50 | 0.94207 | 0.75655 | 0.52923 |
| mAP50-95 | 0.70694 | 0.47432 | 0.36110 |

### EASY-v2.1 Per-Class Test Metrics

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| boat | 0.93942 | 0.60517 | 0.63552 | 0.43812 |
| ship | 0.92898 | 0.89879 | 0.95216 | 0.64519 |
| buoy | 1.00000 | 0.00000 | 0.00000 | 0.00000 |

EASY-v2.1 did not fix the buoy collapse. Buoy recall remained `0.00000` on test. Boat performance degraded strongly. Ship performance remained strong.

## 4. Scientific Conclusion

Removing leakage made the benchmark more rigorous, but the available data did not support robust generalization under strict sequence-safe evaluation.

The remaining issue is not solved by further split tuning. EASY-v2.1 already tested the most direct correction: sequence-safe splitting plus buoy-aware constraints. The result still failed on the held-out test split.

This indicates that the current internal data is not sufficient to build a stronger sequence-safe replacement baseline through additional EASY-v2.x split iterations alone.

## 5. Final Decision

- `EASY-v1-rgb3-buoy-rebalanced` remains the official baseline.
- EASY-v2 and EASY-v2.1 are archived as methodological experiments.
- Dataset iteration stops here.
- No additional EASY-v2.x rebuilds or training runs should be launched.

## 6. Next Recommended Direction

Recommended direction: **A. Finalize report/presentation using EASY-v1.**

Secondary future path: acquire genuinely new buoy/boat data before attempting EASY-v3.

Do not run another EASY-v2 split experiment.
