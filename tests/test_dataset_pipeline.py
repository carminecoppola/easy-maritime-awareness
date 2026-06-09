import base64
import json
import sys
from math import isclose
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.datasets.build_easy_v0 import build_easy_v0  # noqa: E402
from src.datasets.class_mapping import load_dataset_schema, map_original_class  # noqa: E402
from src.datasets.generate_dataset_manifest import generate_dataset_manifest  # noqa: E402
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser  # noqa: E402
from src.datasets.validate_easy_v0 import (  # noqa: E402
    validate_class_ids,
    validate_easy_v0,
    validate_mapping_consistency,
    validate_missing_pairs,
    validate_splits,
)
from src.config import (  # noqa: E402
    DATASET_SCHEMA_PATH,
    EASY_V0_CLASS_NAMES,
    EASY_V0_CLASS_TO_ID,
    EASY_V0_ID_TO_CLASS,
    load_paths_config,
    resolve_storage_paths,
    resolve_storage_root,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5W3fQAAAAASUVORK5CYII="
)


def test_schema_and_storage_config(monkeypatch, tmp_path):
    assert EASY_V0_CLASS_NAMES == ["boat", "ship", "buoy", "debris", "person"]
    assert [EASY_V0_CLASS_TO_ID[name] for name in EASY_V0_CLASS_NAMES] == [0, 1, 2, 3, 4]
    assert EASY_V0_ID_TO_CLASS == {
        0: "boat",
        1: "ship",
        2: "buoy",
        3: "debris",
        4: "person",
    }

    assert map_original_class("SeaShips", "container ship") == "ship"
    assert map_original_class("SMD", "buoy") == "buoy"
    assert map_original_class("smd", "unknown-class") is None

    schema = load_dataset_schema(DATASET_SCHEMA_PATH)
    assert isclose(sum(schema["splits"].values()), 1.0, rel_tol=0.0, abs_tol=1e-9)

    config = load_paths_config()
    assert config["storage"]["env_var"] == "EASY_DATA_ROOT"

    monkeypatch.setenv("EASY_DATA_ROOT", str(tmp_path / "easy-data"))
    root = resolve_storage_root(load_paths_config())
    assert root == tmp_path / "easy-data"

    paths = resolve_storage_paths(load_paths_config())
    assert paths["smd"] == tmp_path / "easy-data" / "raw" / "smd"
    assert paths["easy_v0"] == tmp_path / "easy-data" / "processed" / "EASY-v0"


def test_storage_root_defaults_to_repo_local_data(monkeypatch):
    monkeypatch.delenv("EASY_DATA_ROOT", raising=False)
    root = resolve_storage_root(load_paths_config())
    assert root == PROJECT_ROOT / "data"


def test_parsers_and_staging_layout(monkeypatch, tmp_path):
    monkeypatch.setenv("EASY_DATA_ROOT", str(tmp_path / "easy-data"))
    parser = SMDParser()
    structure = parser.expected_raw_structure()
    assert structure["dataset_key"] == "smd"
    assert structure["required_directories"]
    assert MassMINDParser().thermal_only is True
    assert MassMINDParser().modality == "thermal"

    for parser_cls in [SMDParser, SeaShipsParser, MassMINDParser]:
        current = parser_cls()
        assert current.images_dir.name == "images"
        assert current.annotations_dir.name == "annotations"

    result = parser.validate_staging_layout()
    assert result["valid"] is False
    assert result["errors"]


def test_smd_and_other_parsers_read_minimal_records(monkeypatch, tmp_path):
    data_root = tmp_path / "easy-data"
    monkeypatch.setenv("EASY_DATA_ROOT", str(data_root))

    smd_images = data_root / "raw" / "smd" / "images"
    smd_annotations = data_root / "raw" / "smd" / "annotations"
    smd_images.mkdir(parents=True)
    smd_annotations.mkdir(parents=True)
    (smd_images / "frame_001.png").write_bytes(PNG_1X1)
    (smd_annotations / "frame_001.json").write_text(
        json.dumps(
            {
                "image_filename": "frame_001.png",
                "width": 640,
                "height": 480,
                "objects": [{"class_name": "buoy", "bbox_xyxy": [10, 20, 110, 220]}],
            }
        ),
        encoding="utf-8",
    )
    smd_records = list(SMDParser().iter_annotation_records())
    assert len(smd_records) == 1
    assert smd_records[0]["objects"][0]["easy_class"] == "buoy"

    seaships_images = data_root / "raw" / "seaships" / "images"
    seaships_annotations = data_root / "raw" / "seaships" / "annotations"
    seaships_splits = data_root / "raw" / "seaships" / "source_downloads" / "ImageSets" / "Main"
    seaships_images.mkdir(parents=True)
    seaships_annotations.mkdir(parents=True)
    seaships_splits.mkdir(parents=True)
    (seaships_images / "ship_001.png").write_bytes(PNG_1X1)
    (seaships_annotations / "ship_001.xml").write_text(
        """<annotation>
  <filename>ship_001.png</filename>
  <size><width>800</width><height>600</height></size>
  <object>
    <name>container ship</name>
    <bndbox><xmin>30</xmin><ymin>40</ymin><xmax>230</xmax><ymax>240</ymax></bndbox>
  </object>
    </annotation>""",
        encoding="utf-8",
    )
    (seaships_splits / "train.txt").write_text("ship_001\n", encoding="utf-8")
    (seaships_splits / "val.txt").write_text("", encoding="utf-8")
    (seaships_splits / "test.txt").write_text("", encoding="utf-8")
    seaships_records = list(SeaShipsParser().iter_annotation_records())
    assert len(seaships_records) == 1
    assert seaships_records[0]["objects"][0]["easy_class"] == "ship"
    assert seaships_records[0]["split"] == "train"

    massmind_images = data_root / "raw" / "massmind" / "images"
    massmind_annotations = data_root / "raw" / "massmind" / "annotations"
    massmind_images.mkdir(parents=True)
    massmind_annotations.mkdir(parents=True)
    (massmind_images / "thermal_001.png").write_bytes(PNG_1X1)
    (massmind_annotations / "thermal.csv").write_text(
        "image_filename,width,height,original_class,xmin,ymin,xmax,ymax\n"
        "thermal_001.png,320,240,Living Obstacle,5,10,60,100\n",
        encoding="utf-8",
    )
    massmind_records = list(MassMINDParser().iter_annotation_records())
    assert len(massmind_records) == 1
    assert massmind_records[0]["objects"][0]["easy_class"] == "person"


def test_massmind_parser_reads_segmentation_pairs(monkeypatch, tmp_path):
    data_root = tmp_path / "easy-data"
    monkeypatch.setenv("EASY_DATA_ROOT", str(data_root))

    massmind_images = data_root / "raw" / "massmind" / "images"
    massmind_semantic = data_root / "raw" / "massmind" / "annotations" / "semantic"
    massmind_instance = data_root / "raw" / "massmind" / "annotations" / "instance"
    massmind_images.mkdir(parents=True)
    massmind_semantic.mkdir(parents=True)
    massmind_instance.mkdir(parents=True)

    Image.fromarray(np.array([[10, 20], [30, 40]], dtype=np.uint8), mode="L").save(
        massmind_images / "thermal_a.png"
    )
    Image.fromarray(np.array([[3, 3], [4, 0]], dtype=np.uint8), mode="L").save(
        massmind_semantic / "thermal_a.png"
    )
    Image.fromarray(np.array([[1, 1], [2, 3]], dtype=np.uint16), mode="I;16").save(
        massmind_instance / "thermal_a.png"
    )

    records = list(MassMINDParser().iter_annotation_records())
    assert len(records) == 1
    assert records[0]["width"] == 2
    assert records[0]["height"] == 2
    assert len(records[0]["objects"]) == 3

    by_original = {obj["original_class"]: obj for obj in records[0]["objects"]}
    assert by_original["Obstacle"]["easy_class"] == "debris"
    assert by_original["Living Obstacle"]["easy_class"] == "person"
    assert by_original["Sky"]["easy_class"] is None


def test_dataset_manifest_counts(monkeypatch, tmp_path):
    data_root = tmp_path / "easy-data"
    monkeypatch.setenv("EASY_DATA_ROOT", str(data_root))
    images_dir = data_root / "raw" / "smd" / "images"
    annotations_dir = data_root / "raw" / "smd" / "annotations"
    images_dir.mkdir(parents=True)
    annotations_dir.mkdir(parents=True)
    (images_dir / "a.png").write_bytes(PNG_1X1)
    (annotations_dir / "a.json").write_text(
        json.dumps(
            {
                "image_filename": "a.png",
                "width": 100,
                "height": 100,
                "objects": [{"class_name": "buoy", "bbox_xyxy": [1, 2, 10, 20]}],
            }
        ),
        encoding="utf-8",
    )
    manifest = generate_dataset_manifest(dataset="smd")
    assert manifest["presence_status"] in ["partial", "ready"]
    assert manifest["image_count"] == 1
    assert manifest["annotation_count"] == 1
    assert manifest["parse_preview"]


def test_validation_and_build_simulation(monkeypatch, tmp_path):
    schema = __import__("src.config", fromlist=["load_dataset_schema"]).load_dataset_schema()
    assert validate_class_ids(schema)["valid"] is True
    assert validate_splits(schema)["valid"] is True
    assert validate_mapping_consistency(schema)["valid"] is True

    data_root = tmp_path / "easy-data"
    monkeypatch.setenv("EASY_DATA_ROOT", str(data_root))
    (data_root / "raw" / "smd").mkdir(parents=True)
    (data_root / "raw" / "seaships").mkdir(parents=True)
    (data_root / "raw" / "massmind").mkdir(parents=True)
    (data_root / "manifests").mkdir(parents=True)
    (data_root / "logs").mkdir(parents=True)

    validation = validate_easy_v0(mode="filesystem-light")
    assert validation["valid"] is True
    assert validation["warnings"]

    build = build_easy_v0(
        paths_path=PROJECT_ROOT / "configs" / "paths.yaml",
        simulate=True,
        manifest_path=data_root / "manifests" / "build.json",
        report_path=data_root / "logs" / "build.md",
    )
    manifest = build["manifest"]
    assert manifest["metadata"]["mode"] == "simulation"
    assert manifest["merge_result"]["mode"] == "simulation"


def test_real_easy_v0_build_writes_merged_outputs(monkeypatch, tmp_path):
    data_root = tmp_path / "easy-data"
    monkeypatch.setenv("EASY_DATA_ROOT", str(data_root))

    smd_images = data_root / "raw" / "smd" / "images"
    smd_annotations = data_root / "raw" / "smd" / "annotations"
    smd_images.mkdir(parents=True)
    smd_annotations.mkdir(parents=True)
    (smd_images / "frame_001.png").write_bytes(PNG_1X1)
    (smd_annotations / "frame_001.json").write_text(
        json.dumps(
            {
                "image_filename": "frame_001.png",
                "width": 640,
                "height": 480,
                "objects": [{"class_name": "buoy", "bbox_xyxy": [10, 20, 110, 220]}],
                "notes": ["source_sequence_id=SMD_SEQ_A"],
                "source_sequence_id": "SMD_SEQ_A",
            }
        ),
        encoding="utf-8",
    )

    seaships_images = data_root / "raw" / "seaships" / "images"
    seaships_annotations = data_root / "raw" / "seaships" / "annotations"
    seaships_splits = data_root / "raw" / "seaships" / "source_downloads" / "ImageSets" / "Main"
    seaships_images.mkdir(parents=True)
    seaships_annotations.mkdir(parents=True)
    seaships_splits.mkdir(parents=True)
    (seaships_images / "ship_001.png").write_bytes(PNG_1X1)
    (seaships_annotations / "ship_001.xml").write_text(
        """<annotation>
  <filename>ship_001.png</filename>
  <size><width>800</width><height>600</height></size>
  <object>
    <name>container ship</name>
    <bndbox><xmin>30</xmin><ymin>40</ymin><xmax>230</xmax><ymax>240</ymax></bndbox>
  </object>
</annotation>""",
        encoding="utf-8",
    )
    (seaships_splits / "train.txt").write_text("ship_001\n", encoding="utf-8")
    (seaships_splits / "val.txt").write_text("", encoding="utf-8")
    (seaships_splits / "test.txt").write_text("", encoding="utf-8")

    massmind_images = data_root / "raw" / "massmind" / "images"
    massmind_semantic = data_root / "raw" / "massmind" / "annotations" / "semantic"
    massmind_instance = data_root / "raw" / "massmind" / "annotations" / "instance"
    massmind_images.mkdir(parents=True)
    massmind_semantic.mkdir(parents=True)
    massmind_instance.mkdir(parents=True)
    Image.fromarray(np.array([[10, 20], [30, 40]], dtype=np.uint8), mode="L").save(
        massmind_images / "thermal_a.png"
    )
    Image.fromarray(np.array([[3, 3], [4, 0]], dtype=np.uint8), mode="L").save(
        massmind_semantic / "thermal_a.png"
    )
    Image.fromarray(np.array([[1, 1], [2, 3]], dtype=np.uint16), mode="I;16").save(
        massmind_instance / "thermal_a.png"
    )

    result = build_easy_v0(
        paths_path=PROJECT_ROOT / "configs" / "paths.yaml",
        simulate=False,
        manifest_path=data_root / "manifests" / "build.json",
        report_path=data_root / "logs" / "build.md",
    )

    manifest = result["manifest"]
    assert manifest["metadata"]["mode"] == "real"
    assert manifest["merge_result"]["rgb_summary"]["image_count"] == 2
    assert manifest["merge_result"]["massmind_companion_summary"]["record_count"] == 1
    assert (data_root / "processed" / "EASY-v0" / "dataset.yaml").exists()


def test_validate_missing_pairs(tmp_path):
    dataset_dir = tmp_path / "processed" / "EASY-v0"
    image_dir = dataset_dir / "images" / "train"
    label_dir = dataset_dir / "labels" / "train"
    image_dir.mkdir(parents=True)
    label_dir.mkdir(parents=True)
    (image_dir / "sample.jpg").write_text("image", encoding="utf-8")
    (label_dir / "orphan.txt").write_text("0 0.5 0.5 0.1 0.1", encoding="utf-8")
    result = validate_missing_pairs(dataset_dir)
    assert result["warnings"]
    assert result["details"]["missing_labels"] == ["train/sample"]
    assert result["details"]["missing_images"] == ["train/orphan"]
