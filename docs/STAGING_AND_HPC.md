# Staging and HPC Workflow

## Active Local Storage Policy

Repository-tracked code and docs live in Git. Local datasets and generated artifacts do not.

Treat these as local-only areas:

- `data/`
- `outputs/`
- `models/`
- `archive/`

## Active Dataset Entry Point

The only active processed dataset entry point is:

- `data/processed/EASY-v0-rgb3-balanced-v2/dataset.yaml`

The repository no longer treats older processed dataset variants as active.

## Active Training Surface

The only active SLURM training job kept in the cleaned repository is:

- `scripts/slurm/train_rgb3_balanced_v2_yolov8n.sbatch`

This job is the canonical path for:

- balanced-v2 training
- balanced-v2 validation
- balanced-v2 report generation

## Output Conventions

- run artifacts: `outputs/runs/rgb3_balanced_v2_baseline/`
- reports: `outputs/reports/`
- current forensic gallery: `outputs/error_analysis/boat_vs_buoy/`
- local archives: `archive/`

## Cleanup Rule

If a local dataset, script, report, or job does not support the active balanced-v2 workflow, it should live in `archive/` rather than in the active repository surface.

## Raw Data Rule

Everything under `data/raw/` is preserved and must not be removed by repository cleanup.
