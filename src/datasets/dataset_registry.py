"""
Unified dataset metadata, planning, and lightweight conversion readiness helpers.
"""

from pathlib import Path
from typing import Optional, Union

from src.config import get_storage_sources, resolve_storage_paths
from src.datasets.class_mapping import is_supported_original_class, load_dataset_schema


DATASET_SPECS = {
    "smd": {
        "dataset_name": "Singapore Maritime Dataset (SMD)",
        "official_sources": [
            "https://sites.google.com/site/dilipprasad/home/singapore-maritime-dataset",
        ],
        "required_items": [
            "visible and/or infrared source folders",
            "ground-truth annotations",
            "metadata/readme from source release",
        ],
        "license_todo": "Confirm legal usage terms before downloading or redistributing.",
        "source_format": "custom-video-annotations",
        "rgb_merge_candidate": True,
        "thermal_companion": False,
    },
    "seaships": {
        "dataset_name": "SeaShips",
        "official_sources": [
            "https://github.com/jiaming-wang/SeaShips",
        ],
        "required_items": [
            "dataset archive or extracted image folders",
            "annotation files or label metadata",
            "upstream readme/license notes",
        ],
        "license_todo": "Confirm repository-linked dataset redistribution terms before use.",
        "source_format": "custom-bbox",
        "rgb_merge_candidate": True,
        "thermal_companion": False,
    },
    "massmind": {
        "dataset_name": "MassMIND",
        "official_sources": [
            "https://github.com/uml-marine-robotics/MassMIND",
        ],
        "required_items": [
            "thermal imagery folders",
            "annotation masks/metadata",
            "upstream readme/license notes",
        ],
        "license_todo": "Confirm dataset usage rights before staging into shared storage.",
        "source_format": "thermal-segmentation",
        "rgb_merge_candidate": False,
        "thermal_companion": True,
        "extra_manifest_notes": [
            "MassMIND is validated as a thermal companion only.",
            "MassMIND is not included in the RGB/YOLO merge simulation for v1.",
        ],
    },
}


def _get_spec(dataset_key):
    if dataset_key not in DATASET_SPECS:
        raise KeyError("Unsupported dataset_key: {}".format(dataset_key))
    return DATASET_SPECS[dataset_key]


def get_download_plan(dataset_key, paths_config=None):
    spec = _get_spec(dataset_key)
    storage_sources = get_storage_sources(paths_config)
    raw_dir = storage_sources[dataset_key]
    return {
        "dataset_key": dataset_key,
        "dataset_name": spec["dataset_name"],
        "automatic_download": False,
        "official_sources": list(spec["official_sources"]),
        "expected_raw_dir": str(raw_dir),
        "required_items": list(spec["required_items"]),
        "license_todo": spec["license_todo"],
    }


def validate_raw_layout(dataset_key, raw_dir: Optional[Union[str, Path]] = None, paths_config=None):
    storage_sources = get_storage_sources(paths_config)
    target_dir = Path(raw_dir) if raw_dir is not None else storage_sources[dataset_key]
    errors = []
    warnings = []

    if not target_dir.exists():
        errors.append("Raw dataset directory does not exist: {}".format(target_dir))
    elif not any(target_dir.iterdir()):
        warnings.append("Raw dataset directory exists but is empty: {}".format(target_dir))

    return {
        "dataset_key": dataset_key,
        "expected_raw_dir": str(target_dir),
        "exists": target_dir.exists(),
        "errors": errors,
        "warnings": warnings,
    }


def print_manual_instructions(dataset_key, paths_config=None):
    plan = get_download_plan(dataset_key, paths_config=paths_config)
    lines = [
        "Manual download required for {}".format(plan["dataset_name"]),
        "Target directory: {}".format(plan["expected_raw_dir"]),
        "Official sources:",
    ]
    lines.extend("- {}".format(url) for url in plan["official_sources"])
    lines.append("Automatic download is intentionally disabled in pipeline v1.")
    return "\n".join(lines)


def scan_source_dataset(dataset_key, raw_dir: Optional[Union[str, Path]] = None, paths_config=None):
    storage_sources = get_storage_sources(paths_config)
    target_dir = Path(raw_dir) if raw_dir is not None else storage_sources[dataset_key]
    spec = _get_spec(dataset_key)
    return {
        "dataset_key": dataset_key,
        "raw_dir": str(target_dir),
        "exists": target_dir.exists(),
        "is_empty": target_dir.exists() and not any(target_dir.iterdir()),
        "source_format": spec["source_format"],
    }


def build_conversion_manifest(dataset_key, schema_path=None, paths_config=None):
    schema = load_dataset_schema(schema_path)
    storage_paths = resolve_storage_paths(paths_config)
    spec = _get_spec(dataset_key)
    mapped_classes = [
        source_name
        for source_name in schema["class_mapping"][dataset_key]
        if is_supported_original_class(dataset_key, source_name, schema_path)
    ]
    manifest = {
        "dataset_key": dataset_key,
        "source_format": spec["source_format"],
        "expected_raw_dir": str(storage_paths[dataset_key]),
        "interim_dir": str(storage_paths["interim"] / dataset_key),
        "target_format": schema["dataset"]["format"],
        "mapped_classes": mapped_classes,
        "rgb_merge_candidate": bool(spec["rgb_merge_candidate"]),
        "conversion_mode": "simulation-only",
    }
    if spec["thermal_companion"]:
        manifest["thermal_companion"] = True
        manifest["notes"] = list(spec.get("extra_manifest_notes", []))
    return manifest


def simulate_conversion(dataset_key, schema_path=None, paths_config=None):
    scan = scan_source_dataset(dataset_key, paths_config=paths_config)
    manifest = build_conversion_manifest(dataset_key, schema_path=schema_path, paths_config=paths_config)
    spec = _get_spec(dataset_key)

    if dataset_key == "massmind":
        readiness = "partial" if scan["exists"] else "blocked"
        notes = list(manifest.get("notes", []))
        if not scan["exists"]:
            notes.append("Raw dataset missing; thermal staging not ready.")
        elif scan["is_empty"]:
            notes.append("Raw dataset directory is empty; source contents still need staging.")
        else:
            notes.append("Thermal source present, but downstream mapping remains restricted.")
    else:
        readiness = "ready" if scan["exists"] else "blocked"
        notes = []
        if not scan["exists"]:
            notes.append("Raw dataset missing; conversion not runnable yet.")
        elif scan["is_empty"]:
            readiness = "partial"
            notes.append("Raw dataset directory is empty; source contents still need staging.")

    return {
        "dataset_key": dataset_key,
        "readiness": readiness,
        "scan": scan,
        "manifest": manifest,
        "notes": notes,
    }


def simulate_merge(conversion_manifests, processed_easy_v0_dir, include_rgb=None, thermal_companions=None):
    include_rgb = include_rgb or ["smd", "seaships"]
    thermal_companions = thermal_companions or ["massmind"]
    processed_dir = Path(processed_easy_v0_dir)

    readiness = dict((item["dataset_key"], item["readiness"]) for item in conversion_manifests)
    included_rgb = [key for key in include_rgb if key in readiness]
    thermal = [key for key in thermal_companions if key in readiness]
    excluded = [item["dataset_key"] for item in conversion_manifests if item["dataset_key"] not in included_rgb + thermal]

    ready_rgb = [key for key in included_rgb if readiness.get(key) == "ready"]
    blocked_rgb = [key for key in included_rgb if readiness.get(key) != "ready"]

    return {
        "mode": "simulation",
        "target_dir": str(processed_dir),
        "expected_structure": {
            "images": ["train", "val", "test"],
            "labels": ["train", "val", "test"],
        },
        "rgb_merge_datasets": included_rgb,
        "thermal_companions": thermal,
        "excluded_from_rgb_merge": excluded,
        "readiness": readiness,
        "notes": [
            "No files are copied in simulation mode.",
            "MassMIND is carried only as a thermal companion in v1.",
        ],
        "summary": {
            "ready_rgb_datasets": ready_rgb,
            "blocked_rgb_datasets": blocked_rgb,
            "thermal_companion_datasets": thermal,
        },
    }
