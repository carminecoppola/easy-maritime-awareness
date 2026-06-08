"""
Lightweight validators for EASY-v0 dataset preparation.
"""

import argparse
from math import isclose
from pathlib import Path

from src.config import (
    get_storage_sources,
    load_dataset_schema,
    load_paths_config,
    resolve_storage_paths,
)
from src.datasets.generate_dataset_manifest import generate_dataset_manifest
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser


def _result(name, errors=None, warnings=None, details=None):
    return {
        "name": name,
        "valid": not errors,
        "errors": errors or [],
        "warnings": warnings or [],
        "details": details or {},
    }


def validate_class_ids(schema):
    classes = schema["classes"]
    ids = [entry["id"] for entry in classes]
    expected = list(range(len(classes)))
    errors = []
    if ids != expected:
        errors.append("Class IDs must be contiguous and ordered: {}".format(expected))
    return _result("class_ids", errors=errors, details={"ids": ids, "expected": expected})


def validate_mapping_consistency(schema):
    errors = []
    warnings = []
    allowed = set(entry["name"] for entry in schema["classes"])

    for dataset_name, mapping in schema.get("class_mapping", {}).items():
        for source_class, target_class in mapping.items():
            if target_class not in allowed:
                errors.append(
                    "Dataset '{}' maps '{}' to unsupported class '{}'".format(
                        dataset_name, source_class, target_class
                    )
                )
        if not mapping:
            warnings.append("Dataset '{}' has an empty mapping".format(dataset_name))

    return _result("mapping_consistency", errors=errors, warnings=warnings)


def validate_splits(schema):
    splits = schema["splits"]
    split_sum = sum(float(value) for value in splits.values())
    errors = []
    if not isclose(split_sum, 1.0, rel_tol=0.0, abs_tol=1e-9):
        errors.append("Split sum must be 1.0, got {:.6f}".format(split_sum))
    return _result("splits", errors=errors, details={"splits": splits, "sum": split_sum})


def validate_raw_dataset_presence(paths_config=None):
    sources = get_storage_sources(paths_config)
    warnings = []
    details = {}

    for dataset_name, dataset_path in sources.items():
        details[dataset_name] = {
            "path": str(dataset_path),
            "exists": dataset_path.exists(),
            "empty": dataset_path.exists() and not any(dataset_path.iterdir()),
        }
        if not dataset_path.exists():
            warnings.append("Raw dataset missing: {} ({})".format(dataset_name, dataset_path))

    return _result("raw_dataset_presence", warnings=warnings, details=details)


def validate_staging_layout(paths_config=None, schema_path=None, paths_path=None):
    parser_instances = [
        SMDParser(schema_path=schema_path, paths_path=paths_path),
        SeaShipsParser(schema_path=schema_path, paths_path=paths_path),
        MassMINDParser(schema_path=schema_path, paths_path=paths_path),
    ]

    warnings = []
    details = {}
    for parser in parser_instances:
        manifest = parser.build_parse_manifest()
        details[parser.dataset_key] = manifest
        warnings.extend(manifest["layout"]["errors"])
        warnings.extend(manifest["layout"]["warnings"])

    return _result("staging_layout", warnings=warnings, details=details)


def validate_manifest_generation(paths_config=None, schema_path=None, paths_path=None):
    manifest = generate_dataset_manifest(
        dataset="all",
        schema_path=schema_path,
        paths_path=paths_path,
    )
    warnings = []
    for dataset_key, entry in manifest.items():
        if entry["presence_status"] != "ready":
            warnings.append(
                "Dataset manifest for '{}' is not fully ready: {}".format(
                    dataset_key, entry["presence_status"]
                )
            )
        if entry["parse_preview_error"]:
            warnings.append(
                "Dataset manifest for '{}' has parse preview error: {}".format(
                    dataset_key, entry["parse_preview_error"]
                )
            )
    return _result("manifest_generation", warnings=warnings, details=manifest)


def validate_processed_layout(processed_easy_v0_dir):
    dataset_dir = Path(processed_easy_v0_dir)
    warnings = []
    details = {"dataset_dir": str(dataset_dir), "splits": {}}

    for split in ["train", "val", "test"]:
        image_dir = dataset_dir / "images" / split
        label_dir = dataset_dir / "labels" / split
        details["splits"][split] = {
            "image_dir": str(image_dir),
            "label_dir": str(label_dir),
            "images_exist": image_dir.exists(),
            "labels_exist": label_dir.exists(),
        }
        if not image_dir.exists():
            warnings.append("Missing images directory: {}".format(image_dir))
        if not label_dir.exists():
            warnings.append("Missing labels directory: {}".format(label_dir))

    return _result("processed_layout", warnings=warnings, details=details)


def validate_missing_pairs(processed_easy_v0_dir):
    dataset_dir = Path(processed_easy_v0_dir)
    warnings = []
    details = {"missing_images": [], "missing_labels": []}
    image_suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    for split in ["train", "val", "test"]:
        image_dir = dataset_dir / "images" / split
        label_dir = dataset_dir / "labels" / split
        if not image_dir.exists() or not label_dir.exists():
            continue

        image_stems = set(
            path.stem for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in image_suffixes
        )
        label_stems = set(
            path.stem for path in label_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".txt"
        )

        for stem in sorted(image_stems - label_stems):
            details["missing_labels"].append("{}/{}".format(split, stem))
        for stem in sorted(label_stems - image_stems):
            details["missing_images"].append("{}/{}".format(split, stem))

    if details["missing_labels"]:
        warnings.append("Some images do not have label files.")
    if details["missing_images"]:
        warnings.append("Some label files do not have matching images.")

    return _result("missing_pairs", warnings=warnings, details=details)


def validate_easy_v0(mode="schema-only", schema_path=None, paths_config=None, paths_path=None):
    schema = load_dataset_schema(schema_path)
    storage_paths = resolve_storage_paths(paths_config)

    checks = [
        validate_class_ids(schema),
        validate_mapping_consistency(schema),
        validate_splits(schema),
    ]

    if mode in ("filesystem-light", "processed-layout"):
        checks.append(validate_raw_dataset_presence(paths_config))
        checks.append(
            validate_staging_layout(
                paths_config=paths_config,
                schema_path=schema_path,
                paths_path=paths_path,
            )
        )
        checks.append(
            validate_manifest_generation(
                paths_config=paths_config,
                schema_path=schema_path,
                paths_path=paths_path,
            )
        )

    if mode == "processed-layout":
        checks.append(validate_processed_layout(storage_paths["easy_v0"]))
        checks.append(validate_missing_pairs(storage_paths["easy_v0"]))

    errors = []
    warnings = []
    for check in checks:
        errors.extend(check["errors"])
        warnings.extend(check["warnings"])

    return {
        "mode": mode,
        "valid": not errors,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Lightweight EASY-v0 validation")
    parser.add_argument(
        "--mode",
        default="schema-only",
        choices=["schema-only", "filesystem-light", "processed-layout"],
    )
    parser.add_argument("--schema-path", default=None)
    parser.add_argument("--paths-path", default=None)
    args = parser.parse_args()

    paths_config = load_paths_config(args.paths_path) if args.paths_path else None
    result = validate_easy_v0(
        mode=args.mode,
        schema_path=args.schema_path,
        paths_config=paths_config,
        paths_path=args.paths_path,
    )
    print(result)


if __name__ == "__main__":
    main()
