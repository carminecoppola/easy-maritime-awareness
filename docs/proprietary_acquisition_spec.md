# Data-acquisition campaign specification — EASY-v3

Results this specification builds on: `outputs/reports/easy_v3_results.md`.

## Collection priorities

| Priority | What | Why |
| --- | --- | --- |
| High | Buoys of the operating area (type, colour, shape, light conditions) | Only 18 buoy sequences in total today (5 EASY + 13 ABOships); open-water recall is still about 4% |
| High | Open water, small and distant objects | The gap isolated on MODD2: 956 annotated obstacles, 37 found by the best model |
| Medium | Adverse conditions (haze, backlight, rough sea) | Under-represented in every current source |
| Medium | False positives from the real context (own hull, piers with people or objects) | So far measured only on generic scenes (16.9% false positives) |
| To be confirmed | Classes `debris` and `person` | In the original schema (`configs/dataset_schema.yaml`), never populated |

## To be defined with the team

- Camera model(s) and optics fitted
- Target resolution and frame rate
- Geographic area(s) and seasonality
- Type of buoys and markers in the area (IALA A/B system, local colours)
- Target number of buoy sequences (minimum reference: 15-20)
- Annotation format and labelling tool
- Available annotation budget

## Requirement: an explicit sequence id

Every outing, day or video must have an identifier assigned at collection time, not
reconstructed afterwards. Minimum manifest per batch:
`sequence_id, date, area, conditions, camera, frame count`.

`scripts/dataset/build_sequence_safe_split.py` already reads a `manifest.csv`
(columns `stem`/`filename` and `sequence_id`) when one is present in the source root.
Missions recorded with the EASY dashboard can be exported (`dataset.json` with a
deterministic split) as raw material; their labels still have to be annotated.

## Delivery format

```
data/external_sources/<batch_name>_v1/
├── images/
├── labels/            # YOLO: class x_center y_center width height
├── manifest.csv       # stem, sequence_id
└── PROVENANCE.md      # date, area, camera, licence/ownership
```

## Next steps

1. Collect the answers to the "To be defined with the team" section.
2. Validate the first batch (even a small one) with the same scheme before scaling up.
