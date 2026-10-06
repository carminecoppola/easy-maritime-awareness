<div align="center">

# EASY · Environmental Awareness by the Sea and beYond

**Maritime object-detection models, sequence-safe dataset tooling and honest validation**

[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)
![Task](https://img.shields.io/badge/task-object%20detection-0a7ea4)
![Classes](https://img.shields.io/badge/classes-boat%20%C2%B7%20ship%20%C2%B7%20buoy-1f6feb)
![Runtime](https://img.shields.io/badge/runtime-ONNX%20·%20Raspberry%20Pi%204-c51a4a)

</div>

EASY detects `boat`, `ship` and `buoy` in RGB images. The model runs on-device, on a
Raspberry Pi 4 with ONNX Runtime and no GPU, inside the
[**EASY Maritime Awareness Dashboard**](https://github.com/carminecoppola/EASY-Maritime-Awareness-Dashboard),
which handles live acquisition, inference, missions and dataset export. This repository
is the other half of the project: how the model was trained, how it is evaluated, and
what its results really mean.

## Why this repository is worth reading

Most of what is here is about **not fooling yourself**:

- The original EASY-v1 split moved images between train, validation and test one by
  one, ignoring the video each came from. 11 of 36 sequences ended up in several sets,
  so the headline mAP50 of 0.942 was inflated. The leak was found, documented and
  fixed.
- Splits are now built by `build_sequence_safe_split.py`, which keeps every sequence in
  a single set and fails the build if it cannot.
- Models are also tested on **MODD2**, an open-water benchmark never used in training,
  and on non-maritime images to measure false positives.

## Current model

| | `easy_v3_aboships_640.onnx` (released) | 960 px variant (not released) |
| --- | ---: | ---: |
| Precision | 0.699 | 0.712 |
| Recall | 0.592 | 0.642 |
| mAP50 | 0.627 | 0.678 |
| mAP50-95 | 0.314 | 0.344 |
| Buoy recall | 0.485 | 0.536 |

Sequence-safe internal test set, trained on SMD + SeaShips + ABOships. Details,
checksums and limits: [`models/MODEL_CARD.md`](models/MODEL_CARD.md).

### Read this before relying on it

| | |
| --- | --- |
| Open water (MODD2, 956 obstacles) | the best model finds **3.87%** |
| Non-maritime images | 16.9% produce a false `ship` (EASY-v1 measurement) |
| Intended use | assisting data collection and research |
| **Not** for | navigation, collision avoidance, any safety-critical use |

The gap on open water is a data problem, not a tuning problem: public datasets barely
cover small, distant objects at sea. The proposed fix is a proprietary acquisition
campaign ([specification](docs/proprietary_acquisition_spec.md)).

## Quick start

```bash
git clone https://github.com/carminecoppola/easy-maritime-awareness.git
cd easy-maritime-awareness
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
shasum -a 256 -c models/checksums.sha256        # verify the released weights
python -m unittest discover -s tests            # run the tests
```

Running the released model needs only ONNX Runtime and the pre/post-processing
described in the model card; a complete, tested implementation is
[`inference_image.py`](https://github.com/carminecoppola/EASY-Maritime-Awareness-Dashboard/blob/main/easy_dashboard/inference_image.py)
in the dashboard repository.

## Reproducing the experiments

```bash
pip install -r requirements-training.txt         # adds Ultralytics (AGPL-3.0)

# 1. Curate ABOships into the flat layout (download the archive from Zenodo first)
python scripts/dataset/curate_aboships.py --zip ABOshipsDataset.zip \
    --output-root data/external_sources/aboships_v1

# 2. Build a sequence-safe split; the leakage audit is mandatory
python scripts/dataset/build_sequence_safe_split.py \
    --source-root data/external_sources/aboships_v1 --source-root <your other source> \
    --output-root data/processed/EASY-v3-aboships-candidate --seed 42

# 3. Train and evaluate (Slurm launchers are in scripts/validation/)
python scripts/validation/train_sequence_safe_candidate.py \
    --dataset-yaml data/processed/EASY-v3-aboships-candidate/dataset.yaml \
    --project outputs/experiments/easy_v3_aboships_candidate \
    --name yolov8n_pretrained_50ep_easy_v3_aboships_candidate

# 4. External validation
python scripts/validation/modd2_external_eval.py --help
python scripts/validation/false_positive_scan.py --help
```

Raw data (SMD, SeaShips, MassMIND) and generated datasets are not distributed here;
`data/` is git-ignored.

## Repository map

```text
models/                 released weights, MODEL_CARD.md, checksums.sha256
scripts/dataset/        sequence-safe split builder, ABOships curation
scripts/validation/     training, MODD2 evaluation, false-positive scan, Slurm launchers
tests/                  tests of the split builder (no sequence shared between sets)
configs/                dataset schema (the original 5-class roadmap, see its header)
docs/                   DATASET, TRAINING_AND_EXPERIMENT_RESULTS, ROADMAP, acquisition spec
outputs/reports/        evaluation reports and raw JSON results
```

Start with [`outputs/reports/easy_v3_results.md`](outputs/reports/easy_v3_results.md)
(the primary report), then [`docs/DATASET.md`](docs/DATASET.md) and
[`docs/ROADMAP.md`](docs/ROADMAP.md).

## The story in one minute

EASY-v0 failed mainly because of its dataset composition. EASY-v1 repaired the buoy
collapse but, because of the leaky split, its numbers could not be trusted. EASY-v2 and
v2.1 removed the leak and exposed the real problem again (buoy recall 0). Adding the
public ABOships dataset to the same leak-free split recovered buoy recall to 0.49-0.54
at two resolutions. On real open water even the best model detects under 4% of
obstacles, so the next step is new data in the real operating domain.

## Citation and credits

If you use this repository, the models or the dashboard in your work, please cite:

> C. Coppola, V. Bucciero, S. Perrotta, R. Montella,
> *An Edge Node for Citizen-Contributed Maritime Observations*,
> INSTIL Workshop, IEEE eScience 2026, Naples.

Machine-readable metadata is in [`CITATION.cff`](CITATION.cff) (GitHub shows a
*Cite this repository* button). The poster *An Instrumented Edge Node for Dual-Sensor
Maritime Safety Monitoring* (IEEE eScience 2026, Best Poster Award, participants'
selection) describes the complete system.

## Licence

Code and original documentation: **BSD 3-Clause**, © 2026 Carmine Coppola and EASY
contributors. You may use, modify and redistribute them provided the copyright notice
and licence text are kept, and you may not use the author's name to endorse derived
products without written permission. For anything beyond that, or if in doubt, ask:
open an issue or contact the author through GitHub ([@carminecoppola](https://github.com/carminecoppola)).

The BSD licence does **not** extend to third-party material. The datasets (ABOships is
CC BY 4.0 and requires attribution to Åbo Akademi University) and the weights, which
derive from Ultralytics YOLOv8 (AGPL-3.0), keep their own terms: see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
