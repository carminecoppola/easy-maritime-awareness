# EASY Dataset Documentation

## ⚠️ Sequence-level leakage in EASY-v1 (read first)

`EASY-v1-rgb3-buoy-rebalanced`'s official split has a **sequence-level data
leakage**: the split-assignment file has a `sequence` column that was not
respected during the buoy-rebalancing pass — 1,127 images were moved between
splits image-by-image, ignoring which video/source sequence they belonged
to. Result: 11 of 36 sequences ended up split across train/val/test (e.g.
`smd:MVI_1469_VIS` appears in all three). This explains the anomalous boat
recall jump between validation (0.43) and test (0.88), and means **every
EASY-v1 metric in this document is inflated and does not represent real
generalization**. Full analysis: `outputs/reports/easy_v3_results.md`.

It is kept below only as a frozen historical record. See "Deployed & Best
Available Models" for the corrected, currently-relevant story.

## Deployed & Best Available Models

Two models exist beyond the leakage-affected EASY-v1, both trained on a
**sequence-safe split** (grouped strictly by source sequence, never by
image) with the public **ABOships** dataset added on top of SMD + SeaShips.
Script: `scripts/dataset/build_sequence_safe_split.py`. Curation:
`scripts/dataset/curate_aboships.py`. Full comparison and methodology:
`outputs/reports/easy_v3_results.md`.

| | Deployed today (`best.onnx`, per dashboard `docs/project-status.md`) | Best available candidate (not yet deployed) |
| --- | --- | --- |
| Resolution | 640px | 960px |
| Precision | 0.699 | 0.712 |
| Recall | 0.592 | 0.642 |
| mAP50 | 0.627 | 0.678 |
| mAP50-95 | 0.314 | 0.344 |
| Boat recall | — (not recorded at 640) | 0.651 |
| Buoy recall | 0.485 | 0.536 |
| Weights | not in this repo | `outputs/experiments/easy_v3_aboships_candidate/yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960/weights/best.pt` |

For reference, the same sequence-safe split *without* ABOships (i.e. only
resolving the leakage, no new data) scored mAP50 0.382 and **buoy recall
0.000** — ABOships is what recovers buoy detection at all.

**Recommendation:** the 960px + ABOships candidate outperforms the currently
deployed 640px model on every metric and should replace it — this has not
happened yet as of this writing.

### External validation on MODD2 (open water, never trained on)

482 sampled frames across 28 sequences, 956 annotated obstacles, class-agnostic
recall at IoU 0.3:

| Model | Recall |
| --- | ---: |
| EASY-v1 (official, leakage-affected) | 1.05% |
| Best available candidate (960px + ABOships) | 3.87% |

Verified not a pipeline artifact: ground-truth boxes correctly aligned, true
positives are coherent (e.g. a nearby dinghy correctly detected), false
negatives are genuinely tiny/distant obstacles on the horizon. **This is a
large, real domain gap — neither model is validated for open-water
deployment.** Raw data: `outputs/reports/easy_v1_modd2_external_eval.json`,
`outputs/reports/easy_v3_aboships960_modd2_external_eval.json`.

### Known failure mode: false positives on non-maritime scenes

124 non-maritime images (filtered COCO128) were run through the official
EASY-v1 model: **16.9% produced at least one false positive** at the
operating threshold (confidence ≥ 0.25), and every single false positive was
classified `ship` (zero `boat`, zero `buoy`). Example: a canopy bed
classified `ship` at 0.83 confidence. Raw data:
`outputs/reports/easy_v1_false_positive_scan.json`. Script:
`scripts/validation/false_positive_scan.py`.

## Official Frozen Baseline (historical, leakage-affected)

The official EASY-v1 dataset is:

`data/processed/EASY-v1-rgb3-buoy-rebalanced`

This dataset is frozen. Do not edit images, labels, splits, or reported metrics in place.

## Class Schema

| ID | Class |
| ---: | --- |
| 0 | boat |
| 1 | ship |
| 2 | buoy |

## Dataset Size (EASY-v1, leakage-affected)

| Split | Images | Objects | Boat | Ship | Buoy |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 7311 | 9829 | 2656 | 4898 | 2275 |
| val | 1567 | 2166 | 478 | 1315 | 373 |
| test | 1567 | 1720 | 529 | 818 | 373 |

Sizing for the sequence-safe + ABOships datasets is not yet documented here —
part of the "recover and land EASY-v3" task below.

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

## Source Datasets

- **Singapore Maritime Dataset (SMD)** — primary RGB maritime source.
- **SeaShips** — supporting RGB source for ship and boat imagery; see the
  [SeaShips paper](https://sites.ucmerced.edu/files/wdu/files/seaship.pdf).
- **ABOships** — added on top of SMD + SeaShips for the sequence-safe models
  only (not part of the frozen EASY-v1 baseline); 9,038 images, 13 sequences,
  CC BY 4.0, Åbo Akademi, [Zenodo DOI 10.5281/zenodo.4736931](https://doi.org/10.5281/zenodo.4736931).
  Class mapping used: `boat`/`sailboat`/`motorboat`/`miscboat` → `boat`;
  `cargoship`/`cruiseship`/`ferry`/`militaryship`/`passengership` → `ship`;
  `seamark` → `buoy` (verified visually).
- **MassMIND (Massachusetts Maritime Infrared Dataset)** — thermal maritime
  companion, reserved for future thermal/multimodal work; see the
  [MassMIND repository](https://github.com/uml-marine-robotics/MassMIND). Not
  used by any current RGB-only model.

## Why EASY-v1 Was Chosen As The Frozen Baseline (historical)

EASY-v0 failed primarily because buoy examples were not distributed well across train, validation, and test.

EASY-v1 appeared to fix that failure by rebalancing buoy-bearing evidence while keeping the model family and training setup stable, producing a test set where buoy performance looked strong:

| Buoy Metric | EASY-v1 Test (leakage-affected) |
| --- | ---: |
| Precision | 0.99862 |
| Recall | 1.00000 |
| mAP50 | 0.99500 |
| mAP50-95 | 0.82777 |

**This result does not hold under the sequence-safe split** — see the
leakage warning at the top of this document. It is kept here only as the
historical reasoning that was believed at the time.

## EASY-v2 And EASY-v2.1 Status

EASY-v2 and EASY-v2.1 are not active datasets.

They were built to test stricter sequence-safe evaluation, using only the
original internal sources (no ABOships yet):

- EASY-v2 removed source-group leakage.
- EASY-v2.1 added buoy-aware split constraints.

Both failed as replacement baselines:

- EASY-v2 test buoy recall: `0.00000`
- EASY-v2.1 test buoy recall: `0.00000`
- EASY-v2.1 boat recall dropped to `0.60517`

Scientific conclusion: removing leakage made the benchmark honest again, but
the internal data alone did not support buoy generalization under it. Adding
ABOships (see "Deployed & Best Available Models" above) is what fixed this —
that step came after EASY-v2/v2.1 and was not yet reflected in this
repository until now.

## Pipeline From Raw Sources

Raw sources (`data/raw/smd`, `data/raw/seaships`, `data/raw/massmind`, ~41GB)
are the only originals kept on disk. Every intermediate stage below is
reproducible from them and was removed from `archive/` to save space.

| Stage | Script | Output (removed) |
| --- | --- | --- |
| 0a | `archive/src/datasets/export_smd_yolo.py --annotations-root data/raw/smd/annotations --output-root data/processed/smd_yolo_full` (raw SMD already extracted/staged in `data/raw/smd/images`+`annotations`, no RAR tool needed to reproduce) | `smd_yolo_full`, `smd_yolo_partial_onboard` |
| 0b | `archive/scripts/build_massmind_thermal_yolo.py` (reads `data/raw/massmind/` directly) | `MassMIND-thermal-yolo` |
| 1 | `archive/src/datasets/build_easy_v0.py` | `EASY-v0` |
| 2 | `archive/scripts/build_easy_v0_rgb3.py --source-root data/processed/EASY-v0 --output-root data/processed/EASY-v0-rgb3` | `EASY-v0-rgb3` |
| 3a | `archive/scripts/build_easy_v0_rgb3_clean_split.py --source-root data/processed/EASY-v0-rgb3 --output-root data/processed/EASY-v0-rgb3-clean` | `EASY-v0-rgb3-clean` (kept, `archive/datasets/EASY-v0-rgb3-clean/`) |
| 3b | `archive/scripts/build_easy_v0_rgb3_balanced_split.py --source-root data/processed/EASY-v0-rgb3 --output-root data/processed/EASY-v0-rgb3-balanced` | `EASY-v0-rgb3-balanced` (removed) |
| 4 | `archive/scripts/build_easy_v0_rgb3_balanced_v2_split.py --source-root data/processed/EASY-v0-rgb3 --output-root data/processed/EASY-v0-rgb3-balanced-v2` | `EASY-v0-rgb3-balanced-v2` |
| 5 | buoy rebalancing → `EASY-v1-rgb3-buoy-rebalanced` (official, leakage introduced here — see warning at top). No versioned script found for this step; see `archive/cleanup_20260618/reports/final_pass/easy_v1_buoy_rebalanced_split_assignments.csv` for the assignment record. |
| 6 | `scripts/dataset/build_sequence_safe_split.py` (from `EASY-v0-rgb3-clean`, always groups by sequence, mandatory leakage audit) | sequence-safe splits (EASY-v2, EASY-v2.1, and the ABOships-augmented candidates) |
| 7 | `scripts/dataset/curate_aboships.py` | ABOships curated into the class schema above |

`EASY-v2`/`EASY-v2.1` (closed, see above) were built from
`EASY-v0-rgb3-clean` via `scripts/dataset/build_sequence_safe_split.py` and
its predecessor `archive/scripts/build_easy_v0_rgb3_balanced_v2_split.py`.

## Data Handling Rules

- Keep EASY-v1 frozen.
- Do not rebuild EASY-v1 in place.
- Do not modify labels manually without creating a new explicitly versioned dataset.
- Do not create another EASY-v2.x split.
- Any new sequence-safe split must go through `scripts/dataset/build_sequence_safe_split.py`'s mandatory leakage audit — never hand-assign splits again.
- Raw sources in `data/raw/` are preserved for traceability.
- Archived v2/v2.1 materials are under `archive/cleanup_20260620_repo_reset/`.
- Generated dataset candidates (thousands of images/hardlinks) are gitignored — see `.gitignore` — keep only scripts, configs and reports in the repo.

## Licensing and Provenance

The repository's BSD 3-Clause License covers the original software and
documentation only. It does not grant new rights over source datasets, images,
annotations or pretrained assets. Every future dataset release must retain the
source name, access conditions, original license and required citation for each
contributing collection. A file may be included in a distributable dataset only
when its original terms permit that use. ABOships is CC BY 4.0 — attribution
to Åbo Akademi is required in any redistribution.

## Future Dataset Work

The 960px + ABOships candidate above already meets several of the criteria
below and is the de-facto `EASY-v3` — it just was never formally landed as
one with full artifacts (exact split manifest, training config, per-class
breakdown for the deployed 640px variant). **That is priority #1**, ahead of
any new dataset iteration.

Minimum requirement for a formally versioned EASY-v3:

- new buoy regimes (ABOships partially addresses this — only 18 buoy
  sequences total today: 5 EASY + 13 ABOships; still ~4% recall on open water)
- new hard boat examples
- clear licensing/access path (ABOships is CC BY 4.0 — attribution required)
- sequence-safe split policy (already used for the deployed model)
- explicit ambiguity policy for boat vs ship

Beyond that, only extend further if genuinely new, legally usable data closes
the MODD2 open-water gap (currently 3.87% obstacle detection at best). A
**proprietary acquisition campaign in the real operating domain**, not more
internal split tuning, is the identified path — see
`docs/proprietary_acquisition_spec.md` for the full specification (priority
targets, data format, and open questions for the team).
