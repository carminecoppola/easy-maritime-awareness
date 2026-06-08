"""
SeaShips staged parser scaffold.
"""

from .base_parser import BaseDatasetParser


class SeaShipsParser(BaseDatasetParser):
    dataset_key = "seaships"
    dataset_name = "SeaShips"
    modality = "rgb"
    source_format = "custom-bbox"
    thermal_only = False
    supported_annotation_suffixes = (".json", ".csv", ".xml")

    def iter_annotation_records(self):
        for annotation_path in sorted(self.annotations_dir.rglob("*")):
            if not annotation_path.is_file():
                continue
            if annotation_path.suffix.lower() not in self.supported_annotation_suffixes:
                continue
            for record in self._parse_annotation_file(annotation_path):
                yield record
