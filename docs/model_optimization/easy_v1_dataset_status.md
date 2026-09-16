# EASY-v1 Dataset Status

> **Historical / superseded.** This documents the EASY-v1 phase-1 run only (leakage-affected, mAP50 0.94207 not trustworthy). For current results see `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` and `outputs/reports/easy_v3_results.md`.

Generated: `2026-06-26T14:35:09.185058Z`

Dataset root: `data/processed/EASY-v1-rgb3-buoy-rebalanced`

## Summary

| Check | Status |
| --- | --- |
| dataset_root_exists | PASS |
| all_splits_exist | PASS |
| all_images_have_labels | PASS |
| all_labels_have_images | PASS |
| no_broken_symlinks | PASS |
| no_empty_labels | PASS |
| no_malformed_rows | PASS |
| pass | PASS |

## Split Counts

| Split | Images | Labels | Objects | Boat | Ship | Buoy | Empty labels | Missing images for labels | Missing labels for images | Malformed rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 7311 | 7311 | 9829 | 2656 | 4898 | 2275 | 0 | 0 | 0 | 0 |
| val | 1567 | 1567 | 2166 | 478 | 1315 | 373 | 0 | 0 | 0 | 0 |
| test | 1567 | 1567 | 1720 | 529 | 818 | 373 | 0 | 0 | 0 | 0 |

## Notes

- Image counting includes only `.jpg`, `.jpeg`, `.png`.
- Cache artifacts such as `.npy` are ignored.
- Full machine-readable audit: `outputs/reports/phase1_artifacts/easy_v1_dataset_status.json`.

## Issue Counts

| Issue | Count |
| --- | ---: |
| broken_symlinks | 0 |
| empty_labels | 0 |
| malformed_rows | 0 |
| missing_images_for_labels | 0 |
| missing_labels_for_images | 0 |

