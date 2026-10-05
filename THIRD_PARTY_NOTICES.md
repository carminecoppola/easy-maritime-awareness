# Third-party notices

The code and documentation of this repository are © 2026 Carmine Coppola and EASY
contributors under the BSD 3-Clause License (see `LICENSE`). That licence does **not**
cover the third-party material below, whose own terms continue to apply.

## Datasets

| Dataset | Use here | Terms and citation |
| --- | --- | --- |
| **ABOships** (Åbo Akademi University) — Zenodo 10.5281/zenodo.4736931 | Training and validation data (curated by `scripts/dataset/curate_aboships.py`) | CC BY 4.0: attribution to Åbo Akademi is required in anything that includes the data or a model trained on it |
| **Singapore Maritime Dataset (SMD)** | Primary RGB source | Check the upstream terms before redistributing any image or annotation |
| **SeaShips** (Shao et al., IEEE TMM 2018) | Supporting RGB source for ship and boat imagery | Check the upstream terms; cite the SeaShips paper |
| **MODD2** (ViCoS, University of Ljubljana) | External validation only, never trained on | Check the upstream terms; cite the MODD2 papers |
| **MassMIND** (UMass Lowell) | Thermal reference for future work, not used by the current RGB weights | Check the upstream terms |
| **COCO128** (filtered) | Non-maritime images for the false-positive scan | COCO terms |

No dataset image or annotation is redistributed by this repository (`data/` is
git-ignored). Anyone who rebuilds a dataset must keep the name, access conditions,
licence and required citation of every collection that contributes to it.

## Software

| Component | Terms |
| --- | --- |
| **Ultralytics YOLOv8** (training and export) | AGPL-3.0 or Ultralytics enterprise licence. Model weights trained and exported with it are covered by the same terms. Not imported by the inference code of the dashboard (ONNX Runtime only). |
| NumPy, SciPy, OpenCV, Pillow, PyYAML | Their respective permissive licences |

## Model weights

`models/easy_v3_aboships_640.onnx` and the legacy `easy_v1_best_rgb.*` derive from
Ultralytics YOLOv8 and from the datasets above. Treat them as AGPL-3.0 material that
also requires the ABOships attribution. This is a good-faith summary, not legal advice:
confirm the terms with the upstream owners for any commercial or redistributed use.
