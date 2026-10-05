# Roadmap and project rules

## Where the project stands

- `EASY-v1-rgb3-buoy-rebalanced` is frozen as a historical record. Its headline
  metrics (mAP50 0.942) are **leakage-inflated** and must not be cited as
  performance.
- The model in use is `models/easy_v3_aboships_640.onnx` (sequence-safe split plus the
  public ABOships dataset, 640 px). It runs in the
  [EASY dashboard](https://github.com/carminecoppola/EASY-Maritime-Awareness-Dashboard).
- A 960 px model trained with the same recipe is better on every metric (mAP50 0.678
  vs 0.627, buoy recall 0.536 vs 0.485) but is **not deployed**: its weights are not in
  this repository and its latency on the Raspberry Pi 4 has not been benchmarked.
- Both models are far from open-water ready: on the external MODD2 benchmark the best
  one detects 3.87% of obstacles. Public data does not cover that domain.

## Next actions

1. Benchmark the 960 px model on the Raspberry Pi 4 (the dashboard repository has the
   harness, `docs/runtime-benchmark.md`). If it fits the latency budget, export it to
   ONNX, add it under `models/` with its checksum and model card entry, and switch the
   dashboard configuration to it.
2. Re-run the false-positive scan on the ABOships models (it has only been measured on
   EASY-v1).
3. Start the proprietary open-water acquisition campaign described in
   [`proprietary_acquisition_spec.md`](proprietary_acquisition_spec.md) and land the
   result as a properly versioned dataset (for instance `EASY-v4`) once real data exists.

## Rules

- Do not cite EASY-v1's mAP50 0.942 as current or real performance.
- Do not modify `EASY-v1-rgb3-buoy-rebalanced` or its recorded metrics.
- Never build a split by hand: always use `scripts/dataset/build_sequence_safe_split.py`
  and its mandatory leakage audit.
- Do not claim open-water readiness: MODD2 says otherwise.
- Keep raw sources and generated candidates out of git (see `.gitignore`); version only
  scripts, configs, reports and the released model files.
- Any new dataset keeps the name, access conditions, original licence and required
  citation of every contributing collection (see
  [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)).

## Model artifacts

Released weights live in `models/` and are described in
[`models/MODEL_CARD.md`](../models/MODEL_CARD.md), including their SHA-256 checksums.
The dashboard keeps its own copy under `runtime/models/`; the two must be byte-identical
(`shasum -a 256 -c models/checksums.sha256` verifies this repository's copy).
