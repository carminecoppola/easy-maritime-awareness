# EASY Training And Experiment Results

## ⚠️ EASY-v3: the real current results (read this first)

The model actually exported as `best.onnx` and running in the dashboard is
**not** the "Official Baseline Result" below — it is a sequence-safe run
(same split methodology as "EASY-v2 Result") with the public ABOships
dataset added on top, at 640px. A better-performing **960px** variant of the
same recipe also exists and is not yet deployed. Full methodology, raw data
pointers and verdict: `outputs/reports/easy_v3_results.md`.

| | Official (leakage) | Sequence-safe, EASY data only | + ABOships, 640px (**deployed**) | + ABOships, 960px (**best available, not deployed**) |
| --- | ---: | ---: | ---: | ---: |
| Precision | 0.915 | 0.522 | 0.699 | 0.712 |
| Recall | 0.918 | 0.369 | 0.592 | 0.642 |
| mAP50 | 0.942 | 0.382 | 0.627 | 0.678 |
| mAP50-95 | 0.707 | 0.238 | 0.314 | 0.344 |
| Boat recall | — | 0.198 | — (not recorded) | 0.651 |
| Buoy recall | — | 0.000 | 0.485 | 0.536 |

ABOships is what recovers buoy recall from 0 to 0.48–0.54; resolution
960 vs 640 gives a real but modest further gain (+10% mAP50-95), not a fix
for the deeper problem below.

### External validation on MODD2 (open water, never trained on)

482 sampled frames, 28 sequences, 956 annotated obstacles, class-agnostic
recall at IoU 0.3:

| Model | Recall |
| --- | ---: |
| EASY-v1 official (leakage-affected) | 1.05% |
| Best available (960px + ABOships) | 3.87% |

Verified not a pipeline artifact (correct GT alignment, coherent true
positives, false negatives are genuinely tiny/distant obstacles). **Public
data does not cover the open-water / small-object regime** — see
`docs/proprietary_acquisition_spec.md` for the proposed fix.

### Known failure mode: false positives on non-maritime scenes

124 non-maritime images (filtered COCO128): 16.9% produced a false positive
at confidence ≥ 0.25, **always classified `ship`** (never `boat`/`buoy`).
Example: a canopy bed at 0.83 confidence. Raw data:
`outputs/reports/easy_v1_false_positive_scan.json`.

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

## Final Scientific Conclusion (superseded — see warning at top of file)

This conclusion was written before the leakage in EASY-v1 was traced to its
root cause and before ABOships was added. It is kept for historical record.

> EASY-v1 remains the final official baseline. EASY-v2 and EASY-v2.1 showed
> that stricter sequence-safe evaluation is scientifically valuable, but the
> currently available internal data does not support robust generalization
> under that stricter benchmark. Dataset iteration stops here.

**Updated conclusion:** EASY-v1's mAP50 0.94207 is leakage-inflated and
should not be cited. EASY-v2/v2.1 correctly diagnosed the buoy-recall problem
under a clean split; adding ABOships fixed it well enough to reach buoy
recall 0.485–0.536 (see "EASY-v3" above). The 960px ABOships variant is the
best model produced so far and should replace the 640px model currently
deployed. Dataset iteration should resume only to close the MODD2 open-water
gap (3.87% detection at best), via new real-world data per
`docs/proprietary_acquisition_spec.md` — not further internal split tuning.

## Canonical Reports

The active reports are:

- `outputs/reports/easy_v3_results.md` — **the current reference report**:
  leakage discovery, sequence-safe + ABOships results, MODD2 external
  validation, false-positive scan, verdict.
- `outputs/reports/easy_dataset_iteration_closure.md` — historical EASY-v1/v2/v2.1 closure (superseded, see warning at top of this file).
- `outputs/reports/easy_v1_test_evaluation.md` — historical.
- `outputs/reports/easy_v1_buoy_rebalanced_report.md` — historical.
- `outputs/reports/repository_final_cleanup_report.md` — historical.

Raw evaluation data backing `easy_v3_results.md`:

- `outputs/reports/easy_v1_modd2_external_eval.json`
- `outputs/reports/easy_v1_false_positive_scan.json`
- `outputs/reports/easy_v3_aboships960_modd2_external_eval.json`

All intermediate reports are archived under:

`archive/cleanup_20260620_repo_reset/reports/`
