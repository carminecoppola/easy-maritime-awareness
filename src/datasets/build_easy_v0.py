"""
EASY-v0 build orchestrator.
"""

import argparse
import json
import os
import random
import shutil
import socket
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from src.config import (
    load_dataset_schema,
    load_paths_config,
    resolve_storage_paths,
)
from src.datasets.convert_to_yolo import intermediate_record_to_yolo_annotations
from src.datasets.generate_dataset_manifest import generate_dataset_manifest
from src.datasets.generate_dataset_yaml import build_dataset_yaml_content, render_dataset_yaml
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser
from src.datasets.validate_easy_v0 import validate_easy_v0


def _default_output_paths(paths_config):
    storage_paths = resolve_storage_paths(paths_config)
    logging_config = paths_config.get("logging", {})
    return {
        "manifest_path": storage_paths["manifests"] / logging_config.get(
            "manifest_name", "easy_v0_build_manifest.json"
        ),
        "report_path": storage_paths["logs"] / logging_config.get(
            "report_name", "easy_v0_build_report.md"
        ),
    }


def _license_status_snapshot():
    return {
        "smd": {"status": "unclear", "documented_in": "docs/dataset_analysis/dataset_licenses.md"},
        "seaships": {"status": "unclear", "documented_in": "docs/dataset_analysis/dataset_licenses.md"},
        "massmind": {"status": "clear", "documented_in": "docs/dataset_analysis/dataset_licenses.md"},
    }


def _prepare_storage_layout(storage_paths):
    created = []
    warnings = []

    directories = [
        storage_paths["root"],
        storage_paths["raw"],
        storage_paths["interim"],
        storage_paths["processed"],
        storage_paths["logs"],
        storage_paths["manifests"],
        storage_paths["easy_v0"],
    ]
    directories.extend([storage_paths["smd"], storage_paths["seaships"], storage_paths["massmind"]])
    directories.extend(
        [
            storage_paths["smd"] / "images",
            storage_paths["smd"] / "annotations",
            storage_paths["seaships"] / "images",
            storage_paths["seaships"] / "annotations",
            storage_paths["massmind"] / "images",
            storage_paths["massmind"] / "annotations",
        ]
    )

    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            created.append(str(directory))
        except OSError as exc:
            warnings.append(
                "Could not create storage directory '{}': {}".format(directory, exc)
            )

    return {"created": created, "warnings": warnings}


def _serialize_paths(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return dict((key, _serialize_paths(item)) for key, item in value.items())
    if isinstance(value, list):
        return [_serialize_paths(item) for item in value]
    return value


def _safe_link_or_copy(src_path, dst_path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists():
        return
    try:
        os.link(src_path, dst_path)
    except OSError:
        shutil.copy2(src_path, dst_path)


def _sequence_group_key(record):
    return (
        record.get("source_sequence_id")
        or record.get("image_id")
        or Path(record["image_path"]).stem
    )


def _assign_missing_splits(records, schema):
    train_ratio = float(schema["splits"]["train"])
    val_ratio = float(schema["splits"]["val"])

    grouped = defaultdict(list)
    for record in records:
        if record.get("split") in {"train", "val", "test"}:
            continue
        grouped[_sequence_group_key(record)].append(record)

    sequence_ids = sorted(grouped.keys())
    rng = random.Random(42)
    rng.shuffle(sequence_ids)

    total = len(sequence_ids)
    train_end = int(round(total * train_ratio))
    val_end = train_end + int(round(total * val_ratio))

    for index, sequence_id in enumerate(sequence_ids):
        if index < train_end:
            split = "train"
        elif index < val_end:
            split = "val"
        else:
            split = "test"
        for record in grouped[sequence_id]:
            record["split"] = split

    for record in records:
        if record.get("split") not in {"train", "val", "test"}:
            record["split"] = "train"

    return records


def _build_rgb_records(schema_path=None, paths_path=None):
    records = []
    for parser_cls in [SMDParser, SeaShipsParser]:
        parser = parser_cls(schema_path=schema_path, paths_path=paths_path)
        records.extend(list(parser.iter_annotation_records()))
    return records


def _build_massmind_summary(schema_path=None, paths_path=None):
    parser = MassMINDParser(schema_path=schema_path, paths_path=paths_path)
    records = list(parser.iter_annotation_records())
    mapped_object_count = 0
    original_class_counter = Counter()
    mapped_class_counter = Counter()

    for record in records:
        for obj in record["objects"]:
            original_class_counter[obj["original_class"]] += 1
            if obj["is_mapped"]:
                mapped_object_count += 1
                mapped_class_counter[obj["easy_class"]] += 1

    return {
        "record_count": len(records),
        "mapped_object_count": mapped_object_count,
        "original_class_counts": dict(sorted(original_class_counter.items())),
        "mapped_class_counts": dict(sorted(mapped_class_counter.items())),
        "notes": [
            "MassMIND remains a thermal companion dataset.",
            "Its mapped objects are summarized here but not mixed into the RGB YOLO export.",
        ],
    }


def _reset_easy_v0_output(target_dir):
    for child_name in ["images", "labels"]:
        child = target_dir / child_name
        if child.exists():
            shutil.rmtree(child)
    dataset_yaml = target_dir / "dataset.yaml"
    if dataset_yaml.exists():
        dataset_yaml.unlink()


def _export_rgb_records(records, target_dir):
    images_root = target_dir / "images"
    labels_root = target_dir / "labels"
    for split in ["train", "val", "test"]:
        (images_root / split).mkdir(parents=True, exist_ok=True)
        (labels_root / split).mkdir(parents=True, exist_ok=True)

    summary = {
        "image_count": 0,
        "label_file_count": 0,
        "annotation_count": 0,
        "splits": {"train": 0, "val": 0, "test": 0},
        "dataset_record_counts": Counter(),
        "dataset_annotation_counts": Counter(),
    }

    for record in records:
        split = record["split"]
        image_src = Path(record["image_path"])
        file_stem = "{}__{}".format(record["dataset_key"], record["image_id"])
        image_dst = images_root / split / (file_stem + image_src.suffix.lower())
        label_dst = labels_root / split / (file_stem + ".txt")

        _safe_link_or_copy(image_src, image_dst)
        yolo_lines = intermediate_record_to_yolo_annotations(record)
        label_dst.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")

        summary["image_count"] += 1
        summary["label_file_count"] += 1
        summary["annotation_count"] += len(yolo_lines)
        summary["splits"][split] += 1
        summary["dataset_record_counts"][record["dataset_key"]] += 1
        summary["dataset_annotation_counts"][record["dataset_key"]] += len(yolo_lines)

    summary["dataset_record_counts"] = dict(sorted(summary["dataset_record_counts"].items()))
    summary["dataset_annotation_counts"] = dict(sorted(summary["dataset_annotation_counts"].items()))
    return summary


def _write_dataset_yaml(target_dir, schema_path=None, paths_config=None):
    content = build_dataset_yaml_content(schema_path=schema_path, paths_config=paths_config)
    content["path"] = str(target_dir)
    import yaml

    output_path = target_dir / "dataset.yaml"
    output_path.write_text(
        yaml.safe_dump(content, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return output_path


def _real_merge(schema_path=None, paths_path=None, paths_config=None):
    schema = load_dataset_schema(schema_path)
    storage_paths = resolve_storage_paths(paths_config)
    target_dir = storage_paths["easy_v0"]

    rgb_records = _build_rgb_records(schema_path=schema_path, paths_path=paths_path)
    rgb_records = _assign_missing_splits(rgb_records, schema)

    _reset_easy_v0_output(target_dir)
    rgb_summary = _export_rgb_records(rgb_records, target_dir)
    dataset_yaml_path = _write_dataset_yaml(target_dir, schema_path=schema_path, paths_config=paths_config)
    massmind_summary = _build_massmind_summary(schema_path=schema_path, paths_path=paths_path)

    return {
        "mode": "real",
        "target_dir": str(target_dir),
        "rgb_summary": rgb_summary,
        "massmind_companion_summary": massmind_summary,
        "dataset_yaml_path": str(dataset_yaml_path),
    }


def build_easy_v0(
    schema_path=None,
    paths_path=None,
    simulate=True,
    manifest_path=None,
    report_path=None,
):
    schema = load_dataset_schema(schema_path)
    paths_config = load_paths_config(paths_path)
    storage_paths = resolve_storage_paths(paths_config)
    storage_layout = _prepare_storage_layout(storage_paths)

    validation = validate_easy_v0(
        mode="filesystem-light",
        schema_path=schema_path,
        paths_config=paths_config,
        paths_path=paths_path,
    )

    parser_manifests = {
        "smd": SMDParser(schema_path=schema_path, paths_path=paths_path).simulate_parse(),
        "seaships": SeaShipsParser(schema_path=schema_path, paths_path=paths_path).simulate_parse(),
        "massmind": MassMINDParser(schema_path=schema_path, paths_path=paths_path).simulate_parse(),
    }
    staged_dataset_manifest = generate_dataset_manifest(
        dataset="all",
        schema_path=schema_path,
        paths_path=paths_path,
    )

    if simulate:
        merge_result = {
            "mode": "simulation",
            "target_dir": str(storage_paths["easy_v0"]),
            "expected_structure": {
                "images": ["train", "val", "test"],
                "labels": ["train", "val", "test"],
            },
            "rgb_merge_datasets": ["smd", "seaships"],
            "thermal_companions": ["massmind"],
            "notes": [
                "No files are copied in simulation mode.",
                "MassMIND is carried only as a thermal companion in v1.",
            ],
        }
        dataset_yaml_preview = build_dataset_yaml_content(
            schema_path=schema_path,
            paths_config=paths_config,
        )
    else:
        merge_result = _real_merge(
            schema_path=schema_path,
            paths_path=paths_path,
            paths_config=paths_config,
        )
        dataset_yaml_preview = render_dataset_yaml(
            schema_path=schema_path,
            paths_config=paths_config,
        )

    warnings = list(validation["warnings"])
    warnings.extend(storage_layout["warnings"])
    todos = [
        "Confirm dataset license terms before download or redistribution.",
        "Review merged RGB dataset before training baseline.",
    ]

    manifest = {
        "manifest_type": "easy_v0_build_manifest",
        "metadata": {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "hostname": socket.gethostname(),
            "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown-user",
            "mode": "simulation" if simulate else "real",
        },
        "schema": {
            "dataset": schema["dataset"],
            "classes": schema["classes"],
            "splits": schema["splits"],
        },
        "storage": _serialize_paths(storage_paths),
        "storage_layout": storage_layout,
        "license_status": _license_status_snapshot(),
        "parser_manifests": parser_manifests,
        "staged_dataset_manifest": staged_dataset_manifest,
        "merge_result": merge_result,
        "dataset_yaml_preview": dataset_yaml_preview,
        "validation": validation,
        "warnings": warnings,
        "todos": todos,
    }

    report_lines = [
        "# EASY-v0 Build Report",
        "",
        "- Mode: `{}`".format(manifest["metadata"]["mode"]),
        "- Schema valid: `{}`".format(validation["valid"]),
        "- Storage root: `{}`".format(storage_paths["root"]),
        "- RGB datasets ready: `smd, seaships`",
        "- Thermal companion: `massmind`",
        "",
        "## Dataset Readiness",
        "- `smd`: `{}`".format(staged_dataset_manifest["smd"]["presence_status"]),
        "- `seaships`: `{}`".format(staged_dataset_manifest["seaships"]["presence_status"]),
        "- `massmind`: `{}`".format(staged_dataset_manifest["massmind"]["presence_status"]),
    ]

    if simulate:
        report_lines.extend(
            [
                "",
                "## Simulation",
                "- Target dir: `{}`".format(merge_result["target_dir"]),
                "- No files were copied.",
            ]
        )
    else:
        rgb_summary = merge_result["rgb_summary"]
        massmind_summary = merge_result["massmind_companion_summary"]
        report_lines.extend(
            [
                "",
                "## Real Merge Output",
                "- Target dir: `{}`".format(merge_result["target_dir"]),
                "- RGB images: `{}`".format(rgb_summary["image_count"]),
                "- RGB labels: `{}`".format(rgb_summary["label_file_count"]),
                "- RGB annotations: `{}`".format(rgb_summary["annotation_count"]),
                "- Split train: `{}`".format(rgb_summary["splits"]["train"]),
                "- Split val: `{}`".format(rgb_summary["splits"]["val"]),
                "- Split test: `{}`".format(rgb_summary["splits"]["test"]),
                "- MassMIND companion records: `{}`".format(massmind_summary["record_count"]),
                "- MassMIND mapped objects: `{}`".format(massmind_summary["mapped_object_count"]),
            ]
        )

    report_lines.extend(
        [
            "",
            "## TODOs",
        ]
    )
    report_lines.extend("- {}".format(item) for item in todos)
    report_text = "\n".join(report_lines) + "\n"

    output_paths = _default_output_paths(paths_config)
    manifest_file = Path(manifest_path) if manifest_path else output_paths["manifest_path"]
    report_file = Path(report_path) if report_path else output_paths["report_path"]
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(_serialize_paths(manifest), indent=2), encoding="utf-8")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report_text, encoding="utf-8")

    return {
        "manifest": manifest,
        "report": report_text,
        "manifest_path": str(manifest_file),
        "report_path": str(report_file),
        "dataset_yaml_preview_text": render_dataset_yaml(
            schema_path=schema_path,
            paths_config=paths_config,
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="EASY-v0 build pipeline")
    parser.add_argument("--schema-path", default=None)
    parser.add_argument("--paths-path", default=None)
    parser.add_argument("--simulate", action="store_true", default=False)
    parser.add_argument("--manifest-path", default=None)
    parser.add_argument("--report-path", default=None)
    args = parser.parse_args()

    result = build_easy_v0(
        schema_path=args.schema_path,
        paths_path=args.paths_path,
        simulate=args.simulate,
        manifest_path=args.manifest_path,
        report_path=args.report_path,
    )
    print(result["report"])


if __name__ == "__main__":
    main()
