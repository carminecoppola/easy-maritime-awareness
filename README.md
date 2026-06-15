# EASY — Environmental Awareness by the Sea and beYond

EASY is a maritime perception repository currently focused on one active RGB workflow:

- active dataset: `data/processed/EASY-v0-rgb3-balanced-v2`
- active training surface: `YOLOv8n` baseline on `balanced-v2`
- active analysis surface: balanced-v2 evaluation, sequence distribution, and boat-vs-buoy forensic analysis

Historical datasets, scripts, SLURM jobs, and reports have been archived locally under `archive/`.

## Active Repository Surface

Keep these files as the canonical project entrypoints:

- `docs/PROJECT_OVERVIEW.md`
- `docs/DATASET_POLICY.md`
- `docs/STAGING_AND_HPC.md`
- `docs/EASY_Project_Progress_Report.md`
- `notebooks/EASY_Project_Progress_Report.ipynb`

The class schema remains defined in:

- `configs/dataset_schema.yaml`

## Active Dataset

The only active processed dataset in this repository is:

- `data/processed/EASY-v0-rgb3-balanced-v2/dataset.yaml`

This is the current RGB baseline reference and the only dataset that should be treated as operational in the cleaned repository state.

## Active Workflow

1. Use the existing `balanced-v2` dataset.
2. Launch training with:
   - `scripts/slurm/train_rgb3_balanced_v2_yolov8n.sbatch`
3. Run validation and report generation through the same balanced-v2 workflow.
4. Use the current reports and notebook for review and discussion.

## Repository Layout

```text
easy-maritime-awareness/
├── configs/
├── docs/
├── notebooks/
├── scripts/
│   └── slurm/
├── src/
├── tests/            # may be empty or minimal after cleanup
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
├── archive/
└── models/
```

## Local-Only Areas

These directories are local working areas and are not part of the Git-tracked project surface:

- `data/`
- `outputs/`
- `models/`
- `archive/`
- `venv/`

## Notes

- `data/raw/` is intentionally untouched by cleanup operations.
- archived material should be recovered from `archive/` rather than reconstructed from the active repo surface.
- the repository no longer treats `EASY-v0`, `rgb3`, `clean`, or `balanced-v1` as active datasets.
