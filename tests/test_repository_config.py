import sys
from math import isclose
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import (  # noqa: E402
    DATASET_SCHEMA_PATH,
    EASY_V0_CLASS_NAMES,
    EASY_V0_CLASS_TO_ID,
    EASY_V0_ID_TO_CLASS,
    load_paths_config,
    resolve_storage_paths,
    resolve_storage_root,
)
from src.datasets.class_mapping import load_dataset_schema, map_original_class  # noqa: E402
from src.datasets.dataset_registry import get_download_plan  # noqa: E402


def test_official_easy_schema_is_stable():
    assert EASY_V0_CLASS_NAMES == ["boat", "ship", "buoy", "debris", "person"]
    assert [EASY_V0_CLASS_TO_ID[name] for name in EASY_V0_CLASS_NAMES] == [0, 1, 2, 3, 4]
    assert EASY_V0_ID_TO_CLASS == {
        0: "boat",
        1: "ship",
        2: "buoy",
        3: "debris",
        4: "person",
    }


def test_mapping_examples_and_split_sum():
    assert map_original_class("SeaShips", "container ship") == "ship"
    assert map_original_class("SMD", "buoy") == "buoy"
    assert map_original_class("smd", "unknown-class") is None
    schema = load_dataset_schema(DATASET_SCHEMA_PATH)
    assert isclose(sum(schema["splits"].values()), 1.0, rel_tol=0.0, abs_tol=1e-9)


def test_paths_config_and_storage_resolution(monkeypatch, tmp_path):
    config = load_paths_config()
    assert "storage" in config
    assert config["storage"]["env_var"] == "EASY_DATA_ROOT"

    monkeypatch.setenv("EASY_DATA_ROOT", str(tmp_path / "easy-data"))
    root = resolve_storage_root(load_paths_config())
    assert root == tmp_path / "easy-data"

    paths = resolve_storage_paths(load_paths_config())
    assert paths["smd"] == tmp_path / "easy-data" / "raw" / "smd"
    assert paths["easy_v0"] == tmp_path / "easy-data" / "processed" / "EASY-v0"


def test_storage_root_fallback_is_external(monkeypatch):
    monkeypatch.delenv("EASY_DATA_ROOT", raising=False)
    monkeypatch.setenv("USER", "easy-user")
    root = resolve_storage_root(load_paths_config())
    assert str(root).startswith("/storage/internal_02/")
    assert "easy-maritime-awareness-data" in str(root)


def test_download_plans_are_manual_only(monkeypatch, tmp_path):
    monkeypatch.setenv("EASY_DATA_ROOT", str(tmp_path / "easy-data"))
    paths_config = load_paths_config()
    for plan in [get_download_plan("smd", paths_config), get_download_plan("seaships", paths_config), get_download_plan("massmind", paths_config)]:
        assert plan["automatic_download"] is False
        assert "expected_raw_dir" in plan
        assert plan["official_sources"]
