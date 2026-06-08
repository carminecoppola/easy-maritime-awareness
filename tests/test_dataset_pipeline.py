import base64
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.datasets.build_easy_v0 import build_easy_v0  # noqa: E402
from src.datasets.generate_dataset_manifest import generate_dataset_manifest  # noqa: E402
from src.datasets.parsers import MassMINDParser, SMDParser, SeaShipsParser  # noqa: E402
from src.datasets.validate_easy_v0 import (  # noqa: E402
    validate_class_ids,
    validate_easy_v0,
    validate_mapping_consistency,
    validate_missing_pairs,
    validate_splits,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5W3fQAAAAASUVORK5CYII="
)


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
    seaships_images.mkdir(parents=True)
    seaships_annotations.mkdir(parents=True)
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
    seaships_records = list(SeaShipsParser().iter_annotation_records())
    assert len(seaships_records) == 1
    assert seaships_records[0]["objects"][0]["easy_class"] == "ship"

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
    assert manifest["merge_plan"]["rgb_merge_datasets"] == ["smd", "seaships"]
    assert manifest["merge_plan"]["thermal_companions"] == ["massmind"]


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
