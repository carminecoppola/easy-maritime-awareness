# Staging and HPC Workflow

## Storage Policy

Repository-tracked code and docs live in Git.
Dataset contents and generated artifacts do not.

Treat these directories as local or external artifacts:
- `data/`
- `outputs/`
- `models/`

Primary storage resolution is controlled by:
- `configs/paths.yaml`
- `EASY_DATA_ROOT` when set

## Staging Principles

Raw staging must be:
- controlled
- source-aware
- non-destructive
- provenance-preserving

Minimum raw layout expectation:
```text
raw/
├── smd/
│   ├── images/
│   └── annotations/
├── seaships/
│   ├── images/
│   └── annotations/
└── massmind/
    ├── images/
    └── annotations/
```

Dataset-specific auxiliary folders may exist, but parser-facing structure must remain understandable.

## HPC Rule

Allowed on frontend/login node:
- source inspection
- lightweight validation
- manifest generation
- parser dry-runs on small inputs
- test execution that does not rewrite tracked files

Must go through SLURM:
- heavy extraction
- large-scale staging
- dataset-wide parsing
- bulk conversion
- statistics over full corpora
- training and GPU workloads

## Current SMD Workflow

Current recommended SMD path:
1. download official visible archives and GT description file into `data/raw/smd/downloads/`
2. inspect archive structure before extraction
3. extract only selected visible material into `data/raw/smd/source_downloads/`
4. stage frame-level images and intermediate JSON into `data/raw/smd/images/` and `data/raw/smd/annotations/`
5. export YOLO-ready subsets into processed local outputs when needed

## Operational Scripts

Relevant helpers currently include:
- `scripts/inspect_smd_downloads.py`
- `scripts/slurm/prepare_dataset.sbatch`
- `scripts/slurm/stage_smd.sbatch`

These scripts are operational helpers; they do not redefine the project policy.

The active scheduler surface is intentionally minimal: prepare dataset, stage SMD, build simulation, validate layout.
