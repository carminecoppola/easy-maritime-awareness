# EASY — Environmental Awareness by the Sea and beYond

EASY is a maritime perception project focused on building a **clean, reproducible dataset pipeline** for early multimodal object detection.

The current repository is centered on:
- dataset policy and taxonomy for `EASY-v0`
- controlled staging of official source datasets
- intermediate annotation normalization
- YOLO export and merged dataset build
- HPC-safe processing workflows

It is **not** a training-first repository. Training remains a thin downstream baseline over the prepared dataset.

## Current Project Status

Current canonical status:
- official taxonomy frozen in `configs/dataset_schema.yaml`
- official datasets: `SMD` (primary RGB), `SeaShips` (support RGB), `MassMIND` (thermal companion)
- lightweight staging, parsing, intermediate conversion, YOLO export, and merged RGB build are implemented
- the local merged RGB dataset `data/processed/EASY-v0` is ready for baseline training
- a minimal SLURM-safe baseline training entrypoint is available
- an initial CPU smoke training run has been executed successfully via SLURM
- GPU baseline training still requires a cluster-compatible CUDA/PyTorch stack

## Repository Guide

Use these files as the only active project documentation:
- `docs/PROJECT_OVERVIEW.md` — project vision, current status, roadmap
- `docs/DATASET_POLICY.md` — taxonomy, official datasets, mapping and dataset decisions
- `docs/STAGING_AND_HPC.md` — staging rules, storage layout, SLURM/HPC workflow
- `docs/INTERMEDIATE_AND_YOLO_FORMATS.md` — intermediate record format and YOLO export behavior

The single source of truth for class IDs and mappings is:
- `configs/dataset_schema.yaml`

## Repository Structure

```text
easy-maritime-awareness/
├── configs/        # Canonical configuration and taxonomy
├── docs/           # Active canonical docs
├── scripts/        # Minimal operational helpers and SLURM jobs
├── src/            # Dataset-core code only
├── tests/          # Automated tests
├── data/           # Canonical dataset workspace for this repository
├── outputs/        # Local outputs only (ignored / non-canonical)
└── models/         # Local model artifacts only (ignored / non-canonical)
```

## Working Rules

- use `data/` in this repository as the default dataset root
- use `EASY_DATA_ROOT` only when you intentionally want to override that default
- treat `outputs/` and `models/` as local artifacts, not as part of the canonical repository surface
- use the frontend/login node only for lightweight validation and job preparation
- use SLURM for heavy staging, extraction, parsing, conversion, and training
- SLURM logs must live under `outputs/logs/<job-name>/`
- do not redefine taxonomy or class IDs outside `configs/dataset_schema.yaml`

## Typical Workflow

1. Inspect official dataset policy
2. Stage source datasets in a controlled way
3. Convert raw annotations into intermediate records
4. Export YOLO-ready labels and dataset structure
5. Build and validate the merged `EASY-v0` dataset
6. Run baseline training via SLURM

## Notes on Archived Material

Historical documentation and removed non-core code should be recovered from Git history if ever needed.
