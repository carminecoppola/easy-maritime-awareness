# Intermediate and YOLO Formats

## Intermediate Record Format

The intermediate format is the canonical bridge between raw source annotations and YOLO export.

Each record represents one image and preserves:
- dataset provenance
- source annotation path
- image identity
- mapped and original classes
- bounding boxes in absolute coordinates
- source-specific attributes when useful

Core fields include:
- `dataset_key`
- `dataset_name`
- `image_id`
- `image_path`
- `width`
- `height`
- `modality`
- `objects`

Optional metadata may include:
- source sequence ID
- source frame index
- notes
- source view name

## Mapping Behavior

For each object:
- `original_class` preserves the upstream label
- `easy_class` is the official mapped class or `null`
- `class_id` follows the frozen EASY-v0 ID order
- `is_mapped` explicitly marks whether the object survives conversion

Objects without official mapping must remain unmapped rather than forced into a class.

## YOLO Export Rules

YOLO export is derived from intermediate records.

Rules:
- only mapped objects are exported
- class IDs must match `configs/dataset_schema.yaml`
- bounding boxes are normalized from absolute image coordinates
- split assignment should avoid leakage when multiple frames belong to the same source sequence

## Current SMD Export Behavior

Current SMD export pipeline:
1. `.mat` object annotations are normalized into intermediate JSON records
2. annotated frames are materialized as images
3. intermediate JSON is converted to YOLO label files
4. dataset YAML is generated for the exported subset

This supports partial per-dataset exports before full EASY-v0 merge.
