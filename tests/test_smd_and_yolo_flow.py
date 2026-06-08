import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scripts.inspect_smd_downloads import build_archive_summary, normalize_sequence_stem  # noqa: E402
from src.datasets.convert_to_yolo import (  # noqa: E402
    intermediate_record_to_yolo_annotations,
    summarize_intermediate_to_yolo,
)
from src.datasets.export_smd_yolo import (  # noqa: E402
    assign_sequence_splits,
    build_smd_dataset_yaml_content,
    export_records_to_yolo,
)
from src.datasets.smd_mat import normalize_smd_class_name  # noqa: E402


PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010804000000b51c0c020000000b4944415478da63fcff1f0003030200ee56ddf40000000049454e44ae426082"
)


def _record(image_path, sequence_id, frame_idx, class_id):
    return {
        "dataset_key": "smd",
        "dataset_name": "Singapore Maritime Dataset",
        "image_id": image_path.stem,
        "image_path": str(image_path),
        "width": 100,
        "height": 100,
        "modality": "rgb",
        "objects": [
            {
                "original_class": "Boat",
                "easy_class": "boat",
                "class_id": class_id,
                "is_mapped": True,
                "bbox_xyxy": [10, 10, 20, 20],
                "bbox_xywh": [10, 10, 10, 10],
                "attributes": {},
            }
        ],
        "source_sequence_id": sequence_id,
        "source_frame_index": frame_idx,
    }


def test_smd_helpers_cover_aliases_and_archive_shape():
    assert normalize_smd_class_name("Vessel/ship") == "ship"
    assert normalize_smd_class_name("Speed boat") == "boat"
    assert normalize_smd_class_name("Swimming person") == "swimmer"
    assert normalize_smd_class_name("Buoy") == "buoy"

    assert normalize_sequence_stem("MVI_0790_VIS_OB_ObjectGT.mat") == "MVI_0790_VIS_OB"
    assert normalize_sequence_stem("MVI_0788_VIS_OBHorizonGT.mat") == "MVI_0788_VIS_OB"

    entries = [
        {"group": "Videos", "path": "VIS_Onboard/Videos/MVI_0790_VIS_OB.avi", "sequence_stem": "MVI_0790_VIS_OB"},
        {"group": "Videos", "path": "VIS_Onboard/Videos/MVI_0792_VIS_OB.avi", "sequence_stem": "MVI_0792_VIS_OB"},
        {"group": "ObjectGT", "path": "VIS_Onboard/ObjectGT/MVI_0790_VIS_OB_ObjectGT.mat", "sequence_stem": "MVI_0790_VIS_OB"},
        {"group": "TrackGT", "path": "VIS_Onboard/TrackGT/MVI_0790_VIS_OB_TrackGT.mat", "sequence_stem": "MVI_0790_VIS_OB"},
        {"group": "HorizonGT", "path": "VIS_Onboard/HorizonGT/MVI_0790_VIS_OB_HorizonGT.mat", "sequence_stem": "MVI_0790_VIS_OB"},
        {"group": "HorizonGT", "path": "VIS_Onboard/HorizonGT/MVI_0792_VIS_OB_HorizonGT.mat", "sequence_stem": "MVI_0792_VIS_OB"},
    ]
    groups = {
        "Videos": {"MVI_0790_VIS_OB", "MVI_0792_VIS_OB"},
        "HorizonGT": {"MVI_0790_VIS_OB", "MVI_0792_VIS_OB"},
        "ObjectGT": {"MVI_0790_VIS_OB"},
        "TrackGT": {"MVI_0790_VIS_OB"},
    }
    summary = build_archive_summary(entries, groups, "VIS_Onboard.zip", "VIS_Onboard")
    assert summary["missing_vs_videos"]["ObjectGT"] == ["MVI_0792_VIS_OB"]
    assert summary["object_ready_sequences"] == ["MVI_0790_VIS_OB"]


def test_intermediate_to_yolo_summary():
    record = {
        "width": 640,
        "height": 480,
        "objects": [
            {"is_mapped": True, "class_id": 2, "bbox_xyxy": [10, 20, 110, 220]},
            {"is_mapped": False, "class_id": None, "bbox_xyxy": [0, 0, 10, 10]},
        ],
    }
    lines = intermediate_record_to_yolo_annotations(record)
    assert len(lines) == 1
    assert lines[0].startswith("2 ")
    summary = summarize_intermediate_to_yolo([record])
    assert summary["image_count"] == 1
    assert summary["annotation_count"] == 1


def test_export_records_to_yolo_writes_labels_and_yaml(tmp_path):
    image_a = tmp_path / "frame_a.png"
    image_b = tmp_path / "frame_b.png"
    image_a.write_bytes(PNG_1X1)
    image_b.write_bytes(PNG_1X1)
    records = [_record(image_a, "SEQ_A", 0, 0), _record(image_b, "SEQ_B", 1, 1)]

    split_map = assign_sequence_splits(records, seed=1)
    assert set(split_map.keys()) == {"SEQ_A", "SEQ_B"}

    output_root = tmp_path / "yolo_out"
    summary = export_records_to_yolo(records, output_root, seed=1)
    yaml_content = build_smd_dataset_yaml_content(output_root)

    assert summary["image_count"] == 2
    assert summary["label_file_count"] == 2
    assert sum(summary["splits"].values()) == 2
    assert yaml_content["train"] == "images/train"
    assert yaml_content["nc"] == 5
