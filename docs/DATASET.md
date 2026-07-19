# EASY Dataset Documentation

## Official Dataset

The official EASY dataset is:

`data/processed/EASY-v1-rgb3-buoy-rebalanced`

This dataset is frozen. Do not edit images, labels, splits, or reported metrics in place.

## Class Schema

| ID | Class |
| ---: | --- |
| 0 | boat |
| 1 | ship |
| 2 | buoy |

## Dataset Size

| Split | Images | Objects | Boat | Ship | Buoy |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 7311 | 9829 | 2656 | 4898 | 2275 |
| val | 1567 | 2166 | 478 | 1315 | 373 |
| test | 1567 | 1720 | 529 | 818 | 373 |

## Dataset Structure

```text
data/processed/EASY-v1-rgb3-buoy-rebalanced/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
└── dataset.yaml
```

The dataset uses YOLO label format:

```text
class_id x_center y_center width height
```

All coordinates are normalized to `[0, 1]`.

## Why EASY-v1 Is The Baseline

EASY-v0 failed primarily because buoy examples were not distributed well across train, validation, and test.

EASY-v1 fixed that failure by rebalancing buoy-bearing evidence while keeping the model family and training setup stable. The result was a reproducible test set where buoy performance remained strong:

| Buoy Metric | EASY-v1 Test |
| --- | ---: |
| Precision | 0.99862 |
| Recall | 1.00000 |
| mAP50 | 0.99500 |
| mAP50-95 | 0.82777 |

## EASY-v2 And EASY-v2.1 Status

EASY-v2 and EASY-v2.1 are not active datasets.

They were built to test stricter sequence-safe evaluation:

- EASY-v2 removed source-group leakage.
- EASY-v2.1 added buoy-aware split constraints.

Both failed as replacement baselines:

- EASY-v2 test buoy recall: `0.00000`
- EASY-v2.1 test buoy recall: `0.00000`
- EASY-v2.1 boat recall dropped to `0.60517`

Scientific conclusion:

Removing leakage made the benchmark stricter, but the currently available internal data did not support robust generalization under strict sequence-safe evaluation. Further split tuning is closed.

## Data Handling Rules

- Keep EASY-v1 frozen.
- Do not rebuild EASY-v1 in place.
- Do not modify labels manually without creating a new explicitly versioned dataset.
- Do not create another EASY-v2.x split.
- Raw sources in `data/raw/` are preserved for traceability.
- Archived v2/v2.1 materials are under `archive/cleanup_20260620_repo_reset/`.

## Licensing and Provenance

The repository's BSD 3-Clause License covers the original software and
documentation only. It does not grant new rights over source datasets, images,
annotations or pretrained assets. Every future dataset release must retain the
source name, access conditions, original license and required citation for each
contributing collection. A file may be included in a distributable dataset only
when its original terms permit that use.

## Future Dataset Work

Only attempt a future EASY-v3 if genuinely new, legally usable data becomes available.

Minimum requirement for EASY-v3:

- new buoy regimes
- new hard boat examples
- clear licensing/access path
- sequence-safe split policy
- explicit ambiguity policy for boat vs ship
