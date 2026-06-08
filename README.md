# EASY — Environmental Awareness by the Sea and beYond

EASY is a maritime perception project focused on building a **clean, reproducible dataset pipeline** for early multimodal object detection.

The current repository is centered on:
- dataset policy and taxonomy for `EASY-v0`
- controlled staging of official source datasets
- intermediate annotation normalization
- YOLO export preparation
- HPC-safe processing workflows

It is **not** currently a training-first repository. Training remains downstream of dataset preparation.

## Current Project Status

Current canonical status:
- official taxonomy frozen in `configs/dataset_schema.yaml`
- official datasets: `SMD` (primary RGB), `SeaShips` (support RGB), `MassMIND` (thermal companion)
- lightweight staging, parsing, intermediate conversion, and partial YOLO export are implemented
- no official EASY-v0 full merge has been executed yet
- no official training run has been started yet

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
├── data/           # Local artifacts only (ignored / non-canonical)
├── outputs/        # Local outputs only (ignored / non-canonical)
└── models/         # Local model artifacts only (ignored / non-canonical)
```

## Working Rules

- treat `data/`, `outputs/`, and `models/` as **local artifacts**, not as part of the canonical repository surface
- use the frontend/login node only for lightweight validation and job preparation
- use SLURM for heavy staging, extraction, parsing, conversion, and training
- do not redefine taxonomy or class IDs outside `configs/dataset_schema.yaml`

## Typical Workflow

1. Inspect official dataset policy
2. Stage source datasets in a controlled way
3. Convert raw annotations into intermediate records
4. Export YOLO-ready labels and dataset structure
5. Validate the prepared dataset
6. Only then start training work

## Notes on Archived Material

Historical documentation and removed non-core code should be recovered from Git history if ever needed.
