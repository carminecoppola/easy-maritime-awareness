# EASY-v1 Buoy-Rebalanced Candidate Dataset Report

## Dataset Created

- Path: `data/processed/EASY-v1-rgb3-buoy-rebalanced`
- Creation method: `symlink`
- Source dataset preserved unchanged: `data/processed/EASY-v0-rgb3-balanced-v2`

## Split Summary

| Split | Images | Objects | Boat | Ship | Buoy |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 7311 | 9829 | 2656 | 4898 | 2275 |
| val | 1567 | 2166 | 478 | 1315 | 373 |
| test | 1567 | 1720 | 529 | 818 | 373 |

## Buoy Distribution by Split

| Split | Buoy Images | Buoy Objects | Mean Area | Median Area |
| --- | ---: | ---: | ---: | ---: |
| train | 1569 | 2275 | 0.356% | 0.111% |
| val | 281 | 373 | 0.453% | 0.476% |
| test | 281 | 373 | 0.453% | 0.476% |

## Buoy Area Shift Comparison

| Dataset | Split | Mean Buoy Area | Median Buoy Area |
| --- | --- | ---: | ---: |
| old | train | 0.197% | 0.090% |
| old | val | 0.722% | 0.729% |
| old | test | 0.803% | 0.803% |
| new | train | 0.356% | 0.111% |
| new | val | 0.453% | 0.476% |
| new | test | 0.453% | 0.476% |

## Buoy Sequence Distribution

| Split | Sequence | Buoy Count |
| --- | --- | ---: |
| train | smd:MVI_1474_VIS | 1059 |
| train | smd:MVI_1486_VIS | 495 |
| train | smd:MVI_1469_VIS | 350 |
| train | smd:MVI_1481_VIS | 279 |
| train | smd:MVI_0790_VIS_OB | 92 |
| val | smd:MVI_1474_VIS | 138 |
| val | smd:MVI_1469_VIS | 125 |
| val | smd:MVI_1486_VIS | 55 |
| val | smd:MVI_1481_VIS | 55 |
| test | smd:MVI_1474_VIS | 138 |
| test | smd:MVI_1469_VIS | 125 |
| test | smd:MVI_1486_VIS | 55 |
| test | smd:MVI_1481_VIS | 55 |

## Small/Medium/Large Object Analysis

| Split | Small | Medium | Large |
| --- | ---: | ---: | ---: |
| train | 4655 | 2585 | 2589 |
| val | 698 | 704 | 764 |
| test | 644 | 651 | 425 |

## Known Tradeoffs

- Frame-level splitting was used inside buoy-bearing sequences to reduce the severe buoy size-regime shift.
- This partially relaxes sequence purity for the diagnostic candidate dataset.
- Leakage risk is therefore higher than in the original sequence-held-out split, especially for buoy-bearing SMD sequences.
- Non-buoy images were kept in their current split unless needed to move the overall image ratio closer to 70/15/15.

## Audit Checks

- Images without labels: `0`
- Labels without images: `0`
- Malformed label lines: `0`

## Expected Benefit

- This candidate dataset is suitable as a diagnostic experiment because it directly tests whether buoy failure is primarily caused by split-level buoy scale and regime mismatch.
- It is not a final benchmark split because sequence purity is intentionally relaxed for buoy-bearing frames.

## Next Recommendation

1. Train YOLO on this EASY-v1 internal candidate first.
2. If buoy recall remains unstable after this controlled rebalance, add external buoy/obstacle datasets next rather than iterating only on the split.

## Artifacts

- Metadata CSV: `outputs/reports/easy_v1_buoy_rebalanced_metadata.csv`
- Split assignments CSV: `outputs/reports/easy_v1_buoy_rebalanced_split_assignments.csv`

