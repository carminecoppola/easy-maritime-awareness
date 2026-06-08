"""
Generate the official YOLO dataset.yaml content for EASY-v0.
"""

from pathlib import Path
from typing import Optional, Union

import yaml

from src.config import load_dataset_schema, resolve_storage_paths


def build_dataset_yaml_content(schema_path=None, paths_config=None):
    schema = load_dataset_schema(schema_path)
    storage_paths = resolve_storage_paths(paths_config)

    names = dict((entry["id"], entry["name"]) for entry in schema["classes"])
    return {
        "path": str(storage_paths["easy_v0"]),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(schema["classes"]),
        "names": names,
    }


def render_dataset_yaml(schema_path=None, paths_config=None):
    content = build_dataset_yaml_content(schema_path=schema_path, paths_config=paths_config)
    try:
        return yaml.safe_dump(content, sort_keys=False, default_flow_style=False)
    except TypeError:
        return yaml.safe_dump(content, default_flow_style=False)


def write_dataset_yaml(output_path, schema_path=None, paths_config=None):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        render_dataset_yaml(schema_path=schema_path, paths_config=paths_config),
        encoding="utf-8",
    )
    return output_file
