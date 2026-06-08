"""
Utilities for loading and applying the official EASY-v0 class mapping.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.config import DATASET_SCHEMA_PATH, load_dataset_schema as _load_dataset_schema


def _normalize_dataset_name(dataset_name: str) -> str:
    return dataset_name.strip().lower()


def _normalize_original_class(original_class: str) -> str:
    return original_class.strip().lower()


def load_dataset_schema(schema_path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
    """
    Load the official EASY-v0 dataset schema.
    """
    return _load_dataset_schema(schema_path or DATASET_SCHEMA_PATH)


def get_easy_classes(schema_path: Optional[Union[Path, str]] = None) -> List[str]:
    """
    Return ordered EASY-v0 class names.
    """
    schema = load_dataset_schema(schema_path)
    return [entry["name"] for entry in schema["classes"]]


def get_class_to_id(schema_path: Optional[Union[Path, str]] = None) -> Dict[str, int]:
    """
    Return mapping from EASY-v0 class name to class id.
    """
    schema = load_dataset_schema(schema_path)
    return {entry["name"]: entry["id"] for entry in schema["classes"]}


def get_id_to_class(schema_path: Optional[Union[Path, str]] = None) -> Dict[int, str]:
    """
    Return mapping from EASY-v0 class id to class name.
    """
    schema = load_dataset_schema(schema_path)
    return {entry["id"]: entry["name"] for entry in schema["classes"]}


def map_original_class(
    dataset_name: str,
    original_class: str,
    schema_path: Optional[Union[Path, str]] = None,
) -> Optional[str]:
    """
    Map a dataset-native class name into the EASY-v0 taxonomy.
    """
    schema = load_dataset_schema(schema_path)
    dataset_key = _normalize_dataset_name(dataset_name)
    original_key = _normalize_original_class(original_class)

    dataset_mapping = schema.get("class_mapping", {}).get(dataset_key)
    if not dataset_mapping:
        return None

    normalized_mapping = {
        _normalize_original_class(source_name): target_name
        for source_name, target_name in dataset_mapping.items()
    }
    return normalized_mapping.get(original_key)


def is_supported_original_class(
    dataset_name: str,
    original_class: str,
    schema_path: Optional[Union[Path, str]] = None,
) -> bool:
    """
    Return True when the given dataset-native class has an official EASY-v0 mapping.
    """
    return map_original_class(dataset_name, original_class, schema_path) is not None
