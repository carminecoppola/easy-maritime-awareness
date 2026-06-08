"""
Export staged SMD intermediate JSON records to a YOLO-style dataset tree.
"""

import argparse
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

from src.config import load_dataset_schema
from src.datasets.convert_to_yolo import intermediate_record_to_yolo_annotations


def load_intermediate_records(annotations_root):
    records = []
    for annotation_path in sorted(Path(annotations_root).rglob("*.json")):
        payload = json.loads(annotation_path.read_text(encoding="utf-8"))
        payload["_annotation_path"] = str(annotation_path)
        records.append(payload)
    return records


def assign_sequence_splits(records, schema_path=None, seed=42):
    schema = load_dataset_schema(schema_path)
    train_ratio = float(schema["splits"]["train"])
    val_ratio = float(schema["splits"]["val"])
    grouped = defaultdict(list)

    for record in records:
        sequence_id = record.get("source_sequence_id") or record["image_id"]
        grouped[sequence_id].append(record)

    sequence_ids = sorted(grouped.keys())
    rng = random.Random(seed)
    rng.shuffle(sequence_ids)

    total = len(sequence_ids)
    train_end = int(round(total * train_ratio))
    val_end = train_end + int(round(total * val_ratio))

    split_map = {}
    for index, sequence_id in enumerate(sequence_ids):
        if index < train_end:
            split = "train"
        elif index < val_end:
            split = "val"
        else:
            split = "test"
        split_map[sequence_id] = split

    return split_map


def _safe_copy_image(src_path, dst_path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if dst_path.exists():
            return
        os_link = getattr(__import__("os"), "link")
        os_link(src_path, dst_path)
    except Exception:
        shutil.copy2(src_path, dst_path)


def export_records_to_yolo(records, output_root, schema_path=None, seed=42):
    output_root = Path(output_root)
    split_map = assign_sequence_splits(records, schema_path=schema_path, seed=seed)

    images_root = output_root / "images"
    labels_root = output_root / "labels"
    for split in ["train", "val", "test"]:
        (images_root / split).mkdir(parents=True, exist_ok=True)
        (labels_root / split).mkdir(parents=True, exist_ok=True)

    export_summary = {
        "output_root": str(output_root),
        "image_count": 0,
        "label_file_count": 0,
        "annotation_count": 0,
        "splits": {"train": 0, "val": 0, "test": 0},
        "sequence_split_map": split_map,
    }

    for record in records:
        sequence_id = record.get("source_sequence_id") or record["image_id"]
        split = split_map[sequence_id]
        image_src = Path(record["image_path"])
        image_dst = images_root / split / image_src.name
        label_dst = labels_root / split / (image_src.stem + ".txt")

        _safe_copy_image(image_src, image_dst)
        yolo_lines = intermediate_record_to_yolo_annotations(record)
        label_dst.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")

        export_summary["image_count"] += 1
        export_summary["label_file_count"] += 1
        export_summary["annotation_count"] += len(yolo_lines)
        export_summary["splits"][split] += 1

    return export_summary


def build_smd_dataset_yaml_content(output_root, schema_path=None):
    schema = load_dataset_schema(schema_path)
    return {
        "path": str(Path(output_root)),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(schema["classes"]),
        "names": {entry["id"]: entry["name"] for entry in schema["classes"]},
    }


def write_smd_dataset_yaml(output_root, schema_path=None):
    import yaml

    content = build_smd_dataset_yaml_content(output_root, schema_path=schema_path)
    yaml_path = Path(output_root) / "dataset.yaml"
    yaml_path.write_text(
        yaml.safe_dump(content, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return yaml_path


def main():
    parser = argparse.ArgumentParser(description="Export staged SMD intermediate records to YOLO")
    parser.add_argument("--annotations-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--schema-path", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--manifest-out", default=None)
    args = parser.parse_args()

    records = load_intermediate_records(args.annotations_root)
    summary = export_records_to_yolo(
        records=records,
        output_root=args.output_root,
        schema_path=args.schema_path,
        seed=args.seed,
    )
    yaml_path = write_smd_dataset_yaml(args.output_root, schema_path=args.schema_path)
    summary["dataset_yaml_path"] = str(yaml_path)

    payload = json.dumps(summary, indent=2)
    if args.manifest_out:
        manifest_path = Path(args.manifest_out)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(payload, encoding="utf-8")
        print(str(manifest_path))
        return
    print(payload)


if __name__ == "__main__":
    main()
