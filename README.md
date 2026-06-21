# EASY — Environmental Awareness by the Sea and beYond

EASY is a maritime RGB perception project for detecting:

- `boat`
- `ship`
- `buoy`

The repository is now frozen around one official baseline:

`data/processed/EASY-v1-rgb3-buoy-rebalanced`

Dataset iteration is closed. EASY-v2 and EASY-v2.1 were useful methodological experiments, but they are not official baselines.

## Current Status

| Item | Status |
| --- | --- |
| Official baseline | `EASY-v1-rgb3-buoy-rebalanced` |
| Active model family | YOLOv8n |
| Active dataset branch | Closed |
| EASY-v2 / EASY-v2.1 | Archived methodological experiments |
| Recommended next work | Final report/presentation using EASY-v1 |

## Key Results

EASY-v1 test metrics:

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

## Canonical Documentation

Only three documents should be needed to understand the active project:

- `docs/DATASET.md` — dataset structure, classes, baseline status, and dataset-iteration conclusion
- `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` — training results and experiment history
- `docs/EXECUTION_PLAN.md` — current phase, rules, and next actions

Final reports are kept in:

- `outputs/reports/easy_dataset_iteration_closure.md`
- `outputs/reports/easy_v1_test_evaluation.md`
- `outputs/reports/easy_v1_buoy_rebalanced_report.md`
- `outputs/reports/repository_final_cleanup_report.md`

## Active Repository Shape

```text
configs/
data/
  raw/
  processed/
    EASY-v1-rgb3-buoy-rebalanced/
docs/
models/
outputs/
  experiments/
    easy_v1_buoy_rebalanced/
  reports/
scripts/
src/
archive/
```

## Rules

- Do not modify `data/processed/EASY-v1-rgb3-buoy-rebalanced`.
- Do not modify EASY-v1 weights or reported metrics.
- Do not restart EASY-v2 split iteration.
- Treat EASY-v2 and EASY-v2.1 as archived evidence only.
- Attempt EASY-v3 only if genuinely new buoy/boat data becomes available.

## One-Minute Summary

EASY-v0 failed mainly because of dataset composition. EASY-v1 fixed the buoy collapse and became the strongest reproducible baseline. EASY-v2 removed sequence leakage but failed on test generalization. EASY-v2.1 added buoy-aware constraints but still failed. Therefore, EASY-v1 remains the final official baseline and dataset iteration stops here.
