# EASY — Environmental Awareness by the Sea and beYond

EASY is a maritime RGB perception project for detecting:

- `boat`
- `ship`
- `buoy`

The model is deployed on-device (Raspberry Pi 4, ONNX Runtime, CPU-only) by the
[EASY Maritime Awareness Dashboard](https://github.com/carminecoppola/EASY-Maritime-Awareness-Dashboard),
which runs live acquisition, on-demand inference and mission/event logging on
top of it.

## ⚠️ Read this before citing any metric from this repository

The `EASY-v1-rgb3-buoy-rebalanced` baseline documented further down (mAP50
0.94207) has a **known sequence-level data leakage**: 1,127 images were
moved between train/val/test individually during a buoy-rebalancing pass,
ignoring which source video sequence they belonged to. 11 of 36 sequences
ended up split across sets (e.g. `smd:MVI_1469_VIS` appears in all three).
**That mAP50 figure is inflated and must not be quoted as a real or even a
clean-benchmark result.** Full analysis: `outputs/reports/easy_v3_results.md`.

## Current Models (as of this update)

Two sequence-safe models exist, both trained on SMD + SeaShips + the public
**ABOships** dataset (CC BY 4.0), with a leakage-free split enforced by
`scripts/dataset/build_sequence_safe_split.py`:

| | Deployed today (`best.onnx`, 640px) | Best available (960px, **not yet deployed**) |
| --- | ---: | ---: |
| Precision | 0.699 | 0.712 |
| Recall | 0.592 | 0.642 |
| mAP50 | 0.627 | 0.678 |
| mAP50-95 | 0.314 | 0.344 |
| Boat recall | not recorded | 0.651 |
| Buoy recall | 0.485 | 0.536 |

**The 960px candidate beats the deployed model on every metric and should
replace it** — that swap has not happened as of this writing. Weights:
`outputs/experiments/easy_v3_aboships_candidate/yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960/weights/best.pt`.

For reference, the same sequence-safe split *without* ABOships (leakage
fixed, no new data) scores mAP50 0.382 but **buoy recall 0.000** — ABOships
is what makes buoy detection possible at all.

### The gap that still matters: open water

External validation on **MODD2** (482 frames, 28 sequences, 956 annotated
obstacles, never trained on):

| Model | Recall |
| --- | ---: |
| EASY-v1 official (leakage-affected) | 1.05% |
| Best available (960px + ABOships) | 3.87% |

Verified not a pipeline artifact — this is a real, large domain gap.
**Neither model is validated for open-water / real sea deployment.** The
identified fix is a proprietary acquisition campaign, not more public-data
tuning: see `docs/proprietary_acquisition_spec.md`.

### Known failure mode: false positives off-domain

124 non-maritime images (filtered COCO128) run through the official EASY-v1
model: 16.9% produced a false positive at confidence ≥ 0.25, **always
classified `ship`**. Example: a canopy bed at 0.83 confidence. Not yet
re-tested on the ABOships models. Raw data:
`outputs/reports/easy_v1_false_positive_scan.json`.

## Legacy Baseline: EASY-v1-rgb3-buoy-rebalanced (leakage-affected)

`data/processed/EASY-v1-rgb3-buoy-rebalanced` is kept frozen for
reproducibility and historical record, **not** as a claim of real performance.

EASY-v1 test metrics (leakage-affected split):

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

- `docs/DATASET.md` — dataset structure, classes, sources, and the leakage finding.
- `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` — full training/experiment history, including the sequence-safe + ABOships results at both resolutions.
- `docs/EXECUTION_PLAN.md` — current phase and next actions.
- `docs/proprietary_acquisition_spec.md` — specification for the real-world data collection needed to close the MODD2 gap.
- `outputs/reports/easy_v3_results.md` — **the primary results report**: leakage discovery, full metrics comparison, MODD2 external validation, false-positive scan, verdict.

Historical reports (superseded, EASY-v1/v2/v2.1 era) are kept in:

- `outputs/reports/easy_dataset_iteration_closure.md`
- `outputs/reports/easy_v1_test_evaluation.md`
- `outputs/reports/easy_v1_buoy_rebalanced_report.md`
- `outputs/reports/repository_final_cleanup_report.md`

## Active Repository Shape

```text
configs/
data/
  raw/                                    # SMD, SeaShips, MassMIND originals (~41GB, gitignored)
  processed/
    EASY-v1-rgb3-buoy-rebalanced/         # frozen, leakage-affected
  external_sources/                        # ABOships etc. (gitignored)
  external_validation/                     # MODD2 (gitignored)
docs/
models/
outputs/
  experiments/
  reports/
scripts/
  dataset/                                 # sequence-safe split + ABOships curation
  validation/                              # MODD2 eval, false-positive scan, training launchers
  model_optimization/                      # EASY-v1 phase 1 scripts (historical)
  slurm/                                   # EASY-v1 phase 1 job scripts (historical)
src/
archive/                                   # gitignored, local-only historical work
```

## Rules

- Do not modify `data/processed/EASY-v1-rgb3-buoy-rebalanced` or its reported (leakage-affected) metrics — it stays frozen as a historical record.
- Do not present EASY-v1's mAP50 0.94207 as a real or reproducible result in any new report, paper or poster — it is leakage-inflated.
- Any new split must go through `scripts/dataset/build_sequence_safe_split.py`'s mandatory leakage audit.
- Deploy the 960px ABOships candidate to replace the 640px model currently running, or document explicitly why not.
- Do not claim MODD2/open-water readiness — 3.87% recall is not deployment-ready, regardless of internal benchmark numbers.

## One-Minute Summary

EASY-v0 failed mainly because of dataset composition. EASY-v1 "fixed" the
buoy collapse, but its split had a sequence-level leakage bug, so its
headline mAP50 0.942 is not trustworthy. EASY-v2/v2.1 removed that leakage
and re-exposed the buoy failure (recall 0). Adding the public ABOships
dataset on top of the same leakage-free split recovered buoy recall to
0.48–0.54, at two resolutions (640px deployed, 960px better but not yet
deployed). On real open water (MODD2), even the best model detects only
3.87% of obstacles — public data does not cover that domain. A proprietary
acquisition campaign is specified in `docs/proprietary_acquisition_spec.md`
as the next step.

## Reproducibility

`requirements.txt` declares the supported dependency ranges for development.
An exact environment export, configuration files, model checksums and the
evaluation outputs used in a publication should be preserved together in its
versioned research artifact. Metrics reported for `EASY-v1-rgb3-buoy-rebalanced`
are associated with that frozen, leakage-affected baseline only and must not
be quoted as current performance; see "Current Models" above for what is
actually running and what is the best available candidate.

## License

Repository code and original documentation are distributed under the BSD
3-Clause License; see [`LICENSE`](LICENSE). This license does not relicense
third-party datasets, images, annotations or pretrained components. Their
original licenses, access conditions and citation requirements continue to
apply. Model weights may be redistributed only when their training sources and
upstream framework terms permit it. ABOships is CC BY 4.0 — attribution to
Åbo Akademi is required in any redistribution that includes it or a model
trained on it.
