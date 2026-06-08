"""
MassMIND staged parser scaffold.
"""

from .base_parser import BaseDatasetParser


class MassMINDParser(BaseDatasetParser):
    dataset_key = "massmind"
    dataset_name = "MassMIND"
    modality = "thermal"
    source_format = "thermal-segmentation"
    thermal_only = True
    supported_annotation_suffixes = (".json", ".csv")

    def iter_annotation_records(self):
        for annotation_path in sorted(self.annotations_dir.rglob("*")):
            if not annotation_path.is_file():
                continue
            if annotation_path.suffix.lower() not in self.supported_annotation_suffixes:
                continue
            for record in self._parse_annotation_file(annotation_path):
                yield record
