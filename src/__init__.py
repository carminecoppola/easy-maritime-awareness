"""EASY dataset-core package."""

__version__ = "0.1.0"

try:
    from .config import load_config
except ModuleNotFoundError:  # pragma: no cover - optional legacy entrypoint
    load_config = None

__all__ = ["load_config"]
