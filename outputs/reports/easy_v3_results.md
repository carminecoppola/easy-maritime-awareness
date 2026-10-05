# EASY-v3 — validation and dataset-development results

This is the primary results report of the repository. It supersedes the EASY-v1
numbers.

## 1. Data leakage in the official split (EASY-v1-rgb3-buoy-rebalanced)

`easy_v1_buoy_rebalanced_split_assignments.csv` has a `sequence` column (source
video or block of frames) that was not respected during the buoy-rebalancing
pass: 1,127 images were moved between splits image by image, ignoring the
sequence they belong to. As a result 11 of 36 sequences are split across
train/val/test (e.g. `smd:MVI_1469_VIS` appears in all three).

This explains the anomalous jump in boat recall (0.43 on validation, 0.88 on
test) and the gap between the official metrics and the real performance measured
below.

## 2. False positives on non-maritime scenes

124 non-maritime images (filtered COCO128). 16.9% produce at least one false
positive at the operating threshold (conf >= 0.25), always classified as `ship`
(0 boat, 0 buoy). Example: a canopy bed classified as `ship` with 0.83.

## 3. External validation on MODD2

482 frames sampled from MODD2 (28 sequences, never used in training), 956
annotated obstacles.

| Model | Recall (class-agnostic, IoU 0.3) |
| --- | ---: |
| EASY-v1 official | 1.05% |
| Best EASY-v3 (960 px + ABOships) | 3.87% |

Verified not to be a pipeline artifact: ground-truth boxes are correctly aligned,
true positives are coherent (e.g. a nearby dinghy is detected) and the false
negatives are real obstacles that are tiny or far away on the horizon.

## 4. Sequence-safe split

No versioned script built the official split (probably a removed notebook). It was
rebuilt as `scripts/dataset/build_sequence_safe_split.py`: it always groups by
sequence, never by image, and runs a mandatory leakage audit. It supports several
data sources and, for future collections, an explicit sequence manifest
(`manifest.csv`) instead of inferring the sequence from the file name.

## 5. Training comparison (same YOLOv8n model, same hyper-parameters)

| | Official (leaky) | Sequence-safe, EASY data only | + ABOships, 640 px | + ABOships, 960 px |
| --- | ---: | ---: | ---: | ---: |
| Precision | 0.915 | 0.522 | 0.699 | 0.712 |
| Recall | 0.918 | 0.369 | 0.592 | 0.642 |
| mAP50 | 0.942 | 0.382 | 0.627 | 0.678 |
| mAP50-95 | 0.707 | 0.238 | 0.314 | 0.344 |
| Boat recall | — | 0.198 | — | 0.651 |
| Buoy recall | — | 0.000 | 0.485 | 0.536 |

ABOships (Zenodo 10.5281/zenodo.4736931, CC BY 4.0, Åbo Akademi University): 9,038
images, 13 sequences, class `seamark` -> buoy checked visually. Mapping:
boat/sailboat/motorboat/miscboat -> boat,
cargoship/cruiseship/ferry/militaryship/passengership -> ship, seamark -> buoy.

## Verdict

- The official 0.942 mAP50 is a leakage artifact.
- Public data (ABOships) improves performance substantially inside the training
  domain (boat recall x3, buoy recall from 0 to 0.5+).
- On data from a genuinely different domain (MODD2: open water, small and distant
  objects) the improvement is marginal (1.05% -> 3.87%): the public data available
  does not cover that scenario.
- Resolution 960 vs 640: a real but modest improvement (+10% mAP50-95), not a
  solution.

**Conclusion:** proprietary data collection in the specific operating domain (open
water, small objects, the buoys of the area) is required. The specification is in
`docs/proprietary_acquisition_spec.md`.

## References

- Split: `scripts/dataset/build_sequence_safe_split.py`
- ABOships curation: `scripts/dataset/curate_aboships.py`
- Training: `scripts/validation/train_sequence_safe_candidate.py`
- External validation: `scripts/validation/modd2_external_eval.py`,
  `scripts/validation/false_positive_scan.py`
- Candidate dataset: `data/processed/EASY-v3-aboships-candidate/` (not versioned)
- Best weights: `outputs/experiments/easy_v3_aboships_candidate/yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960/weights/best.pt` (not versioned)
- Raw data (JSON): `outputs/reports/easy_v1_modd2_external_eval.json`,
  `outputs/reports/easy_v1_false_positive_scan.json`,
  `outputs/reports/easy_v3_aboships960_modd2_external_eval.json`
