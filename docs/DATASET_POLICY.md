# Dataset Policy

## Canonical Source of Truth

The class schema and ID ordering remain defined in:

- `configs/dataset_schema.yaml`

If any document disagrees with that file, the configuration file wins.

## Taxonomy

The project taxonomy remains:

- `0` boat
- `1` ship
- `2` buoy
- `3` debris
- `4` person

The active cleaned repository workflow uses only the RGB subset:

- `boat`
- `ship`
- `buoy`

through the current balanced-v2 dataset.

## Active Dataset Policy

The only active processed dataset in this repository is:

- `data/processed/EASY-v0-rgb3-balanced-v2`

This dataset is the sole operational reference for training, validation, and error analysis in the cleaned repo state.

## Active Interpretation Rules

- do not treat `EASY-v0` as the active training dataset
- do not treat `rgb3`, `clean`, or `balanced-v1` as active datasets
- do not treat archived processed datasets as part of the active workflow
- do not mix archived dataset paths back into the main documentation or scripts

## Archived / Future Material

MassMIND and the broader five-class roadmap remain part of the overall EASY story, but they are not part of the active local workflow in this cleaned repository state.

That means:

- thermal companion work is not an active processed dataset path here
- archived datasets should be recovered only when explicitly needed
- the current repository surface is intentionally centered on the balanced-v2 RGB branch
