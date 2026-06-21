# EASY Execution Plan

## Current Phase

Phase: **baseline freeze and final reporting**

The project is no longer in dataset-iteration mode.

Official baseline:

`data/processed/EASY-v1-rgb3-buoy-rebalanced`

## Current Decision

EASY-v1 remains the final official baseline.

EASY-v2 and EASY-v2.1 are closed methodological experiments. Do not run more EASY-v2.x rebuilds or training jobs.

## Immediate Goal

Prepare the final project report or presentation using EASY-v1.

The final narrative should be:

1. EASY-v0 exposed a dataset-composition failure.
2. EASY-v1 fixed buoy collapse through dataset rebalancing.
3. EASY-v1 achieved strong reproducible RGB results.
4. EASY-v2/v2.1 tested stricter sequence-safe evaluation but failed with current internal data.
5. Future progress requires genuinely new data, not more split tuning.

## Active Assets

Use these assets only:

| Purpose | Path |
| --- | --- |
| dataset | `data/processed/EASY-v1-rgb3-buoy-rebalanced` |
| best weights | `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt` |
| test report | `outputs/reports/easy_v1_test_evaluation.md` |
| dataset report | `outputs/reports/easy_v1_buoy_rebalanced_report.md` |
| closure report | `outputs/reports/easy_dataset_iteration_closure.md` |
| cleanup report | `outputs/reports/repository_final_cleanup_report.md` |

## Do Not Do

- Do not modify EASY-v1.
- Do not modify EASY-v1 labels.
- Do not modify EASY-v1 weights.
- Do not change reported EASY-v1 metrics.
- Do not build another EASY-v2.x split.
- Do not train another EASY-v2.x model.
- Do not treat archived v2/v2.1 outputs as active baselines.

## Next Actions

1. Write the final report/presentation around EASY-v1.
2. Use `docs/DATASET.md` for dataset facts.
3. Use `docs/TRAINING_AND_EXPERIMENT_RESULTS.md` for metrics and experiment conclusions.
4. Use `outputs/reports/easy_dataset_iteration_closure.md` for the final decision.
5. If future work resumes, start from new data acquisition planning for EASY-v3, not another split rebuild.

## Future Work Gate

Only reopen dataset development if at least one of these becomes true:

- a verified new buoy dataset is available
- a verified new hard-boat dataset is available
- ABOShips or another boat-rich source becomes legally obtainable
- a new annotation budget exists for ambiguous boat/ship cases

If none of those are true, stay with EASY-v1 and finalize the project.

## Resume Checklist

When returning to this repository, first check:

```bash
find outputs/reports -maxdepth 1 -type f | sort
find data/processed -maxdepth 1 -type d | sort
find data/processed/EASY-v1-rgb3-buoy-rebalanced -xtype l | wc -l
```

Expected state:

- active reports: 4 final reports
- active processed dataset: EASY-v1 only
- broken EASY-v1 symlinks: `0`
