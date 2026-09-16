# EASY Execution Plan

## ⚠️ This plan was stale — read the correction below first

Everything under "Original Plan (superseded)" was written when EASY-v1 was
still believed to be a valid baseline and before ABOships was added. It is
kept for history. The current state and plan are below.

## Current Phase

Phase: **deploy the best model, then close the open-water gap**

The original plan's "Future Work Gate" (below) listed *"ABOShips or another
boat-rich source becomes legally obtainable"* as a condition to reopen
dataset work. That condition was met and acted on: ABOships (CC BY 4.0) was
added on top of a corrected sequence-safe split, producing two models (640px
and 960px). Both are now fully documented in this repository (see
`outputs/reports/easy_v3_results.md`, `docs/DATASET.md`,
`docs/TRAINING_AND_EXPERIMENT_RESULTS.md`).

## Current Decision

- `EASY-v1-rgb3-buoy-rebalanced` stays frozen as a historical record; its
  headline metrics (mAP50 0.94207) are **known leakage-inflated** and must
  not be cited as real performance.
- The **640px sequence-safe + ABOships model is currently deployed**
  (`best.onnx` in the dashboard).
- The **960px sequence-safe + ABOships model outperforms it on every metric**
  (mAP50 0.678 vs 0.627, buoy recall 0.536 vs 0.485) and is the recommended
  replacement.
- Both remain far from open-water ready: MODD2 external recall is only 3.87%
  at best.

## Immediate Goal

1. Deploy the 960px ABOships candidate to the dashboard in place of the
   640px model, or explicitly decide not to and record why (size/latency
   tradeoff on Raspberry Pi 4 — not yet benchmarked here).
2. Keep this repository, not a paragraph in another repository, as the
   source of truth for model results going forward.
3. Scope and start the proprietary open-water acquisition campaign per
   `docs/proprietary_acquisition_spec.md`.

## Active Assets

| Purpose | Path | Status |
| --- | --- | --- |
| deployed model | `best.onnx` (dashboard repo, exported from the 640px candidate) | Deployed |
| best available candidate | `outputs/experiments/easy_v3_aboships_candidate/yolov8n_pretrained_50ep_easy_v3_aboships_candidate_960/weights/best.pt` | Not deployed — recommended upgrade |
| primary results report | `outputs/reports/easy_v3_results.md` | Current |
| split builder | `scripts/dataset/build_sequence_safe_split.py` | Current, use for any future split |
| ABOships curation | `scripts/dataset/curate_aboships.py` | Current |
| MODD2 external eval | `scripts/validation/modd2_external_eval.py` | Current |
| false-positive scan | `scripts/validation/false_positive_scan.py` | Current |
| training launcher (candidate, 640) | `scripts/validation/submit_train_aboships_candidate.sbatch` | Current |
| training launcher (960) | `scripts/validation/submit_train_aboships_960.sbatch` | Current |
| legacy dataset | `data/processed/EASY-v1-rgb3-buoy-rebalanced` | Frozen, leakage-affected |
| legacy weights | `outputs/experiments/easy_v1_buoy_rebalanced/yolov8n_pretrained_50ep_easy_v1_buoy_rebalanced/weights/best.pt` | Historical only |

## Do Not Do

- Do not cite EASY-v1's mAP50 0.94207 as current or real performance.
- Do not modify `EASY-v1-rgb3-buoy-rebalanced` or its recorded (invalid) metrics — keep it as a frozen historical record.
- Do not build another split by hand — always go through `scripts/dataset/build_sequence_safe_split.py`'s leakage audit.
- Do not claim the deployed or candidate model is validated for real sea deployment — MODD2 says otherwise (3.87% detection at best).

## Next Actions

1. Benchmark the 960px candidate's on-device latency/memory on the Raspberry Pi 4 (the dashboard repo's `docs/runtime-benchmark.md` has the harness) before deciding whether to deploy it as-is.
2. If it fits the latency budget, export it to ONNX and replace `best.onnx` in the dashboard.
3. Re-run the false-positive scan (currently only measured on EASY-v1) against the ABOships models.
4. Start the proprietary acquisition campaign per `docs/proprietary_acquisition_spec.md`; land results as a properly versioned `EASY-v4` (or similar) once real open-water data exists.

## Resume Checklist

When returning to this repository, first check:

```bash
find outputs/reports -maxdepth 1 -type f | sort
find data/processed -maxdepth 1 -type d | sort
git log --oneline -5
```

Then check whether the 960px candidate has been deployed to the dashboard
yet (compare the dashboard repo's `docs/project-status.md` model description
against `outputs/reports/easy_v3_results.md` here) — if not, that is still
the top task.

---

## Original Plan (superseded)

The content below is kept verbatim for history. Do not follow it as current
guidance — see the correction at the top of this file.

### Original Current Phase

Phase: **baseline freeze and final reporting**

Official baseline: `data/processed/EASY-v1-rgb3-buoy-rebalanced`

### Original Current Decision

EASY-v1 remains the final official baseline. EASY-v2 and EASY-v2.1 are
closed methodological experiments. Do not run more EASY-v2.x rebuilds or
training jobs.

### Original Immediate Goal

Prepare the final project report or presentation using EASY-v1:

1. EASY-v0 exposed a dataset-composition failure.
2. EASY-v1 fixed buoy collapse through dataset rebalancing.
3. EASY-v1 achieved strong reproducible RGB results.
4. EASY-v2/v2.1 tested stricter sequence-safe evaluation but failed with current internal data.
5. Future progress requires genuinely new data, not more split tuning.

### Original Future Work Gate

Only reopen dataset development if at least one of these becomes true:

- a verified new buoy dataset is available
- a verified new hard-boat dataset is available
- ABOShips or another boat-rich source becomes legally obtainable
- a new annotation budget exists for ambiguous boat/ship cases

If none of those are true, stay with EASY-v1 and finalize the project.
