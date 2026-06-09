"""
Configuration management for EASY project.

Handles loading and validation of YAML configuration files and exposes
shared constants for EASY-v0 dataset taxonomy.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "configs"
DATASET_SCHEMA_PATH = CONFIG_DIR / "dataset_schema.yaml"
PATHS_CONFIG_PATH = CONFIG_DIR / "paths.yaml"


def load_config(config_path: Union[Path, str]) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Dictionary containing configuration parameters

    Raises:
        FileNotFoundError: If config file does not exist
        yaml.YAMLError: If YAML parsing fails
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    return config or {}


def save_config(config: Dict[str, Any], output_path: Union[Path, str]) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Dictionary to save
        output_path: Path where to save the configuration
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as handle:
        try:
            yaml.safe_dump(config, handle, default_flow_style=False, sort_keys=False)
        except TypeError:
            yaml.safe_dump(config, handle, default_flow_style=False)


def load_dataset_schema(schema_path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
    """
    Load the official EASY-v0 dataset schema.

    Args:
        schema_path: Optional override path to the schema file

    Returns:
        Parsed dataset schema dictionary

    Raises:
        FileNotFoundError: If the schema file does not exist
        ValueError: If the schema content is missing required keys
    """
    schema_file = Path(schema_path) if schema_path is not None else DATASET_SCHEMA_PATH

    if not schema_file.exists():
        raise FileNotFoundError(
            "EASY-v0 dataset schema not found. "
            f"Expected file at: {schema_file}"
        )

    schema = load_config(schema_file)
    required_keys = {"dataset", "classes", "splits", "datasets", "class_mapping"}
    missing_keys = required_keys - set(schema.keys())

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Dataset schema is missing required keys: {missing}")

    return schema


def load_paths_config(config_path: Optional[Union[Path, str]] = None) -> Dict[str, Any]:
    """
    Load the EASY storage path configuration.
    """
    config_file = Path(config_path) if config_path is not None else PATHS_CONFIG_PATH

    if not config_file.exists():
        raise FileNotFoundError(
            "EASY paths configuration not found. "
            "Expected file at: {}".format(config_file)
        )

    config = load_config(config_file)
    if "storage" not in config:
        raise ValueError("Paths configuration is missing required key: storage")

    return config


def _resolve_username(paths_config: Optional[Dict[str, Any]] = None) -> str:
    config = paths_config or load_paths_config()
    storage = config.get("storage", {})

    explicit_username = storage.get("username")
    if explicit_username:
        return str(explicit_username)

    for env_name in storage.get("username_env_vars", []):
        env_value = os.environ.get(env_name)
        if env_value:
            return env_value

    return "unknown-user"


def resolve_storage_root(paths_config: Optional[Dict[str, Any]] = None) -> Path:
    """
    Resolve the external dataset storage root using env + fallback policy.
    """
    config = paths_config or load_paths_config()
    storage = config["storage"]

    env_var_name = storage.get("env_var")
    if env_var_name:
        env_root = os.environ.get(env_var_name)
        if env_root:
            return Path(env_root).expanduser()

    explicit_root = storage.get("root")
    if explicit_root:
        explicit_root_path = Path(str(explicit_root)).expanduser()
        if not explicit_root_path.is_absolute():
            explicit_root_path = (PROJECT_ROOT / explicit_root_path).resolve()
        return explicit_root_path

    username = _resolve_username(config)
    template = storage.get("fallback_root_template")
    if not template:
        raise ValueError(
            "Paths configuration must define either storage.root or "
            "storage.fallback_root_template"
        )

    return Path(template.format(username=username)).expanduser()


def resolve_storage_paths(paths_config: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
    """
    Resolve all storage paths defined in `configs/paths.yaml`.
    """
    config = paths_config or load_paths_config()
    storage = config["storage"]

    resolved = {"root": resolve_storage_root(config)}

    templates = {
        "raw": storage.get("raw"),
        "interim": storage.get("interim"),
        "processed": storage.get("processed"),
        "logs": storage.get("logs"),
        "manifests": storage.get("manifests"),
        "easy_v0": storage.get("easy_v0"),
    }

    for key, template in templates.items():
        if not template:
            raise ValueError("Paths configuration is missing storage.{}".format(key))
        resolved[key] = Path(str(template).format(**resolved)).expanduser()

    source_templates = storage.get("sources", {})
    if not source_templates:
        raise ValueError("Paths configuration is missing storage.sources")

    for source_name, template in source_templates.items():
        resolved[source_name] = Path(str(template).format(**resolved)).expanduser()

    return resolved


def get_storage_sources(paths_config: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
    """
    Return resolved raw source dataset directories.
    """
    resolved = resolve_storage_paths(paths_config)
    return {
        "smd": resolved["smd"],
        "seaships": resolved["seaships"],
        "massmind": resolved["massmind"],
    }


_DATASET_SCHEMA = load_dataset_schema()
_PATHS_CONFIG = load_paths_config()
_STORAGE_PATHS = resolve_storage_paths(_PATHS_CONFIG)
EASY_V0_CLASS_NAMES = [entry["name"] for entry in _DATASET_SCHEMA["classes"]]
EASY_V0_CLASS_TO_ID = {entry["name"]: entry["id"] for entry in _DATASET_SCHEMA["classes"]}
EASY_V0_ID_TO_CLASS = {entry["id"]: entry["name"] for entry in _DATASET_SCHEMA["classes"]}
DATA_DIR = _STORAGE_PATHS["root"]
RAW_DATA_DIR = _STORAGE_PATHS["raw"]
PROCESSED_DATA_DIR = _STORAGE_PATHS["processed"]
INTERIM_DATA_DIR = _STORAGE_PATHS["interim"]
LOGS_DIR = _STORAGE_PATHS["logs"]
MANIFESTS_DIR = _STORAGE_PATHS["manifests"]
EASY_V0_DIR = _STORAGE_PATHS["easy_v0"]
