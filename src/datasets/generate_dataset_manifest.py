"""
Lightweight manifest generation for staged EASY datasets.
"""

import argparse
import json
from pathlib import Path

from src.config import load_paths_config
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser


PARSER_REGISTRY = {
    "smd": SMDParser,
    "seaships": SeaShipsParser,
    "massmind": MassMINDParser,
}


def _parser_instance(dataset_key, schema_path=None, paths_path=None):
    parser_cls = PARSER_REGISTRY[dataset_key]
    return parser_cls(schema_path=schema_path, paths_path=paths_path)


def generate_dataset_manifest(dataset="all", schema_path=None, paths_path=None):
    dataset_keys = sorted(PARSER_REGISTRY.keys()) if dataset == "all" else [dataset]
    manifests = {}

    for dataset_key in dataset_keys:
        parser = _parser_instance(dataset_key, schema_path=schema_path, paths_path=paths_path)
        parse_manifest = parser.build_parse_manifest()
        layout = parse_manifest["layout"]
        scan = parse_manifest["scan"]
        preview_records = []
        preview_error = None
        try:
            for index, record in enumerate(parser.iter_annotation_records()):
                preview_records.append(
                    {
                        "image_id": record["image_id"],
                        "object_count": len(record["objects"]),
                        "mapped_object_count": len(
                            [obj for obj in record["objects"] if obj["is_mapped"]]
                        ),
                    }
                )
                if index >= 2:
                    break
        except Exception as exc:
            preview_error = str(exc)

        blockers = list(layout["errors"])
        if preview_error:
            blockers.append(preview_error)

        if blockers:
            status = "missing"
        elif layout["warnings"]:
            status = "partial"
        else:
            status = "ready"

        manifests[dataset_key] = {
            "dataset_key": parser.dataset_key,
            "dataset_name": parser.dataset_name,
            "resolved_raw_path": str(parser.raw_root),
            "presence_status": status,
            "image_count": scan["image_count"],
            "annotation_count": scan["annotation_count"],
            "total_size_bytes": scan["total_size_bytes"],
            "dataset_version": "unknown",
            "warnings": layout["warnings"],
            "blockers": blockers,
            "thermal_only": parser.thermal_only,
            "supported_annotation_suffixes": parse_manifest["supported_annotation_suffixes"],
            "parse_preview": preview_records,
            "parse_preview_error": preview_error,
        }

    if dataset == "all":
        return manifests
    return manifests[dataset]


def write_dataset_manifest(output_path, dataset="all", schema_path=None, paths_path=None):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    manifest = generate_dataset_manifest(
        dataset=dataset,
        schema_path=schema_path,
        paths_path=paths_path,
    )
    output_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate lightweight staged dataset manifests")
    parser.add_argument(
        "--dataset",
        default="all",
        choices=["smd", "seaships", "massmind", "all"],
    )
    parser.add_argument("--schema-path", default=None)
    parser.add_argument("--paths-path", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    manifest = generate_dataset_manifest(
        dataset=args.dataset,
        schema_path=args.schema_path,
        paths_path=args.paths_path,
    )
    if args.output:
        output_file = write_dataset_manifest(
            args.output,
            dataset=args.dataset,
            schema_path=args.schema_path,
            paths_path=args.paths_path,
        )
        print(str(output_file))
    else:
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
