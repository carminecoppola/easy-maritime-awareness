"""
SeaShips staged parser scaffold.
"""

from pathlib import Path

from .base_parser import BaseDatasetParser


class SeaShipsParser(BaseDatasetParser):
    dataset_key = "seaships"
    dataset_name = "SeaShips"
    modality = "rgb"
    source_format = "custom-bbox"
    thermal_only = False
    supported_annotation_suffixes = (".json", ".csv", ".xml")

    @property
    def split_dir(self):
        return self.raw_root / "source_downloads" / "ImageSets" / "Main"

    def _load_split_map(self):
        split_files = {
            "train": self.split_dir / "train.txt",
            "val": self.split_dir / "val.txt",
            "test": self.split_dir / "test.txt",
        }
        split_map = {}
        for split_name, split_file in split_files.items():
            if not split_file.exists():
                continue
            for line in split_file.read_text(encoding="utf-8").splitlines():
                image_id = line.strip()
                if image_id:
                    split_map[image_id] = split_name
        return split_map

    def iter_annotation_records(self):
        split_map = self._load_split_map()
        for annotation_path in sorted(self.annotations_dir.rglob("*")):
            if not annotation_path.is_file():
                continue
            if annotation_path.suffix.lower() not in self.supported_annotation_suffixes:
                continue
            for record in self._parse_annotation_file(annotation_path):
                record["split"] = split_map.get(record["image_id"], record.get("split"))
                yield record
