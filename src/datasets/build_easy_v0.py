"""
Simulation-only EASY-v0 build orchestrator.
"""

import argparse
import json
import os
import socket
from datetime import datetime
from pathlib import Path

from src.config import (
    load_dataset_schema,
    load_paths_config,
    resolve_storage_paths,
)
from src.datasets.generate_dataset_manifest import generate_dataset_manifest
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser
from src.datasets.dataset_registry import simulate_conversion, simulate_merge
from src.datasets.generate_dataset_yaml import build_dataset_yaml_content, render_dataset_yaml
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

    conversions = [
        simulate_conversion("smd", schema_path=schema_path, paths_config=paths_config),
        simulate_conversion("seaships", schema_path=schema_path, paths_config=paths_config),
        simulate_conversion("massmind", schema_path=schema_path, paths_config=paths_config),
    ]

    merge_plan = simulate_merge(conversions, storage_paths["easy_v0"])
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
    dataset_yaml_preview = build_dataset_yaml_content(
        schema_path=schema_path,
        paths_config=paths_config,
    )

    warnings = list(validation["warnings"])
    warnings.extend(storage_layout["warnings"])
    todos = [
        "Stage raw datasets into configured external storage.",
        "Confirm dataset license terms before download or redistribution.",
        "Execute heavy conversion/merge steps only via scheduler-managed jobs.",
    ]

    for conversion in conversions:
        warnings.extend(conversion["notes"])

    manifest = {
        "manifest_type": "easy_v0_build_manifest",
        "metadata": {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "hostname": socket.gethostname(),
            "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown-user",
            "mode": "simulation" if simulate else "lightweight",
        },
        "schema": {
            "dataset": schema["dataset"],
            "classes": schema["classes"],
            "splits": schema["splits"],
        },
        "storage": _serialize_paths(storage_paths),
        "storage_layout": storage_layout,
        "license_status": _license_status_snapshot(),
        "source_datasets": dict(
            (
                item["dataset_key"],
                {
                    "expected_path": item["scan"]["raw_dir"],
                    "exists": item["scan"]["exists"],
                    "status": item["readiness"],
                    "notes": item["notes"],
                },
            )
            for item in conversions
        ),
        "conversion_readiness": dict(
            (item["dataset_key"], item["readiness"]) for item in conversions
        ),
        "staging_readiness": dict(
            (key, value["readiness"]) for key, value in parser_manifests.items()
        ),
        "parser_manifests": parser_manifests,
        "staged_dataset_manifest": staged_dataset_manifest,
        "merge_plan": merge_plan,
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
        "- RGB merge datasets: `{}`".format(", ".join(merge_plan["rgb_merge_datasets"])),
        "- Thermal companion datasets: `{}`".format(", ".join(merge_plan["thermal_companions"])),
        "",
        "## Raw Dataset Presence",
    ]

    for dataset_key, source_info in manifest["source_datasets"].items():
        report_lines.append(
            "- `{}`: exists=`{}`, status=`{}`, path=`{}`".format(
                dataset_key,
                source_info["exists"],
                source_info["status"],
                source_info["expected_path"],
            )
        )

    report_lines.extend(
        [
            "",
            "## Staging Readiness",
            "- `smd`: `{}`".format(parser_manifests["smd"]["readiness"]),
            "- `seaships`: `{}`".format(parser_manifests["seaships"]["readiness"]),
            "- `massmind`: `{}`".format(parser_manifests["massmind"]["readiness"]),
            "",
            "## License Status",
            "- `smd`: `unclear`",
            "- `seaships`: `unclear`",
            "- `massmind`: `clear`",
            "",
            "## Mapping Summary",
            "- Official class order: `{}`".format(
                ", ".join(entry["name"] for entry in schema["classes"])
            ),
            "- MassMIND thermal-only in v1: `True`",
            "",
            "## TODOs",
        ]
    )
    report_lines.extend("- {}".format(item) for item in todos)

    report_text = "\n".join(report_lines) + "\n"

    output_paths = _default_output_paths(paths_config)
    manifest_file = Path(manifest_path) if manifest_path else output_paths["manifest_path"]
    report_file = Path(report_path) if report_path else output_paths["report_path"]
    if manifest_file.parent:
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(json.dumps(_serialize_paths(manifest), indent=2), encoding="utf-8")
    if report_file.parent:
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
    parser = argparse.ArgumentParser(description="Simulation-only EASY-v0 build pipeline")
    parser.add_argument("--schema-path", default=None)
    parser.add_argument("--paths-path", default=None)
    parser.add_argument("--simulate", action="store_true", default=True)
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
