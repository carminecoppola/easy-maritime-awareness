# Dataset Policy

## Canonical Source of Truth

The official taxonomy, class IDs, and mapping rules are defined in:
- `configs/dataset_schema.yaml`

If any document disagrees with that file, the configuration file wins.

## Official EASY-v0 Taxonomy

Frozen EASY-v0 classes:
- `0` boat
- `1` ship
- `2` buoy
- `3` debris
- `4` person

Key boundary rules:
- `boat` and `ship` remain distinct
- `buoy` is not merged into generic obstacle classes
- `debris` remains an official class even if current public coverage is weak
- `person` refers to humans only

## Official Datasets

Current official datasets:
- `SMD` — primary RGB dataset
- `SeaShips` — support RGB dataset
- `MassMIND` — thermal companion dataset

These are the only datasets that should be treated as active EASY-v0 sources in the current repository state.

## Mapping Policy

Mapping must remain explicit and controlled.

Current intended policy:
- SMD contributes RGB vessel / buoy / person evidence through official class remapping
- SeaShips strengthens RGB vessel coverage
- MassMIND is retained as thermal companion material and may require constrained interpretation because its labels are coarser than EASY-v0

Unsupported or discarded source classes must not be silently coerced.

## Important Constraints

Do not change locally:
- class IDs
- class ordering
- taxonomy naming
- dataset roles

Do not assume:
- that every source clip has complete ground truth
- that every upstream annotation format maps one-to-one to EASY-v0
- that thermal labels are class-safe without explicit conversion logic

## Operational Implication

Before any training or full merge:
1. stage only official datasets
2. preserve provenance
3. convert to intermediate format first
4. export YOLO only after mapping validation
