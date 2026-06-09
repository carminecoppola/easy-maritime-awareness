"""
Base parser interfaces for staged EASY-v0 datasets.
"""

import csv
import json
from abc import ABCMeta, abstractmethod
from pathlib import Path
import struct
from xml.etree import ElementTree as ET

from src.config import load_dataset_schema, load_paths_config, resolve_storage_paths
from src.datasets.class_mapping import get_class_to_id, map_original_class


class BaseDatasetParser(object):
    __metaclass__ = ABCMeta

    dataset_key = None
    dataset_name = None
    modality = None
    source_format = "unknown"
    thermal_only = False
    supported_annotation_suffixes = ()

    def __init__(self, schema_path=None, paths_path=None):
        self.schema = load_dataset_schema(schema_path)
        self.paths_config = load_paths_config(paths_path)
        self.storage_paths = resolve_storage_paths(self.paths_config)
        self.raw_root = self.storage_paths[self.dataset_key]
        source_layout = self.paths_config["storage"].get("source_layout", {})
        self.images_subdir_name = source_layout.get("images_subdir", "images")
        self.annotations_subdir_name = source_layout.get("annotations_subdir", "annotations")

    @property
    def images_dir(self):
        return self.raw_root / self.images_subdir_name

    @property
    def annotations_dir(self):
        return self.raw_root / self.annotations_subdir_name

    def expected_raw_structure(self):
        return {
            "dataset_key": self.dataset_key,
            "raw_root": str(self.raw_root),
            "required_directories": [
                str(self.images_dir),
                str(self.annotations_dir),
            ],
            "optional_directories": [],
        }

    def validate_staging_layout(self):
        errors = []
        warnings = []

        if not self.raw_root.exists():
            errors.append("Missing raw root: {}".format(self.raw_root))
        if not self.images_dir.exists():
            errors.append("Missing images directory: {}".format(self.images_dir))
        if not self.annotations_dir.exists():
            errors.append("Missing annotations directory: {}".format(self.annotations_dir))
        if self.images_dir.exists() and not any(self.images_dir.iterdir()):
            warnings.append("Images directory is empty: {}".format(self.images_dir))
        if self.annotations_dir.exists() and not any(self.annotations_dir.iterdir()):
            warnings.append("Annotations directory is empty: {}".format(self.annotations_dir))

        return {
            "dataset_key": self.dataset_key,
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "expected_structure": self.expected_raw_structure(),
        }

    def _iter_files(self, root_path, suffixes=None):
        if not root_path.exists():
            return []
        suffixes = tuple(item.lower() for item in (suffixes or []))
        files = []
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            if suffixes and path.suffix.lower() not in suffixes:
                continue
            files.append(path)
        return files

    def scan_staged_files(self):
        image_files = self._iter_files(
            self.images_dir,
            [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"],
        )
        annotation_files = self._iter_files(
            self.annotations_dir,
            [".json", ".xml", ".csv", ".txt", ".mat", ".png", ".npy"],
        )
        total_size = sum(path.stat().st_size for path in image_files + annotation_files)
        return {
            "dataset_key": self.dataset_key,
            "image_count": len(image_files),
            "annotation_count": len(annotation_files),
            "total_size_bytes": total_size,
            "images_dir": str(self.images_dir),
            "annotations_dir": str(self.annotations_dir),
        }

    def _load_image_size(self, image_path, fallback_width=None, fallback_height=None):
        if fallback_width is not None and fallback_height is not None:
            return int(fallback_width), int(fallback_height)
        with Path(image_path).open("rb") as handle:
            header = handle.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            width, height = struct.unpack(">II", header[16:24])
            return int(width), int(height)
        raise ValueError(
            "Image size could not be inferred for '{}' without explicit width/height".format(
                image_path
            )
        )

    def _find_image_path(self, image_reference=None, image_stem=None):
        if image_reference:
            ref_path = Path(image_reference)
            if ref_path.is_absolute() and ref_path.exists():
                return ref_path
            candidate = self.images_dir / image_reference
            if candidate.exists():
                return candidate

        if image_stem:
            for extension in [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]:
                candidate = self.images_dir / (image_stem + extension)
                if candidate.exists():
                    return candidate
            for candidate in self.images_dir.rglob("*"):
                if candidate.is_file() and candidate.stem == image_stem:
                    return candidate
        return None

    def _bbox_xywh_to_xyxy(self, bbox_xywh):
        x, y, width, height = bbox_xywh
        return [x, y, x + width, y + height]

    def _bbox_xyxy_to_xywh(self, bbox_xyxy):
        x1, y1, x2, y2 = bbox_xyxy
        return [x1, y1, x2 - x1, y2 - y1]

    def _build_object(self, original_class, bbox_xyxy=None, bbox_xywh=None, attributes=None):
        easy_class = map_original_class(self.dataset_key, original_class)
        class_to_id = get_class_to_id()
        if bbox_xyxy is None and bbox_xywh is not None:
            bbox_xyxy = self._bbox_xywh_to_xyxy(bbox_xywh)
        if bbox_xywh is None and bbox_xyxy is not None:
            bbox_xywh = self._bbox_xyxy_to_xywh(bbox_xyxy)
        return {
            "original_class": original_class,
            "easy_class": easy_class,
            "class_id": class_to_id.get(easy_class) if easy_class is not None else None,
            "is_mapped": easy_class is not None,
            "bbox_xyxy": bbox_xyxy,
            "bbox_xywh": bbox_xywh,
            "attributes": attributes or {},
        }

    def _build_record(
        self,
        image_path,
        source_annotation_path,
        objects,
        width=None,
        height=None,
        split=None,
        notes=None,
    ):
        resolved_width, resolved_height = self._load_image_size(image_path, width, height)
        return {
            "dataset_key": self.dataset_key,
            "dataset_name": self.dataset_name,
            "image_id": Path(image_path).stem,
            "image_path": str(image_path),
            "width": int(resolved_width),
            "height": int(resolved_height),
            "modality": self.modality,
            "split": split,
            "source_annotation_path": str(source_annotation_path) if source_annotation_path else None,
            "objects": objects,
            "notes": notes or [],
        }

    def _parse_json_annotation(self, annotation_path):
        payload = json.loads(annotation_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            for item in payload:
                yield self._record_from_mapping(annotation_path, item)
        else:
            yield self._record_from_mapping(annotation_path, payload)

    def _record_from_mapping(self, annotation_path, item):
        image_reference = (
            item.get("image_path")
            or item.get("image_filename")
            or item.get("image")
            or item.get("file_name")
        )
        image_stem = item.get("image_id")
        image_path = self._find_image_path(image_reference=image_reference, image_stem=image_stem)
        if image_path is None:
            raise ValueError(
                "Could not resolve image for annotation '{}'".format(annotation_path)
            )

        objects = []
        for obj in item.get("objects", []):
            original_class = obj.get("original_class") or obj.get("class_name") or obj.get("label")
            bbox_xyxy = obj.get("bbox_xyxy")
            bbox_xywh = obj.get("bbox_xywh") or obj.get("bbox")
            if original_class is None and (
                "easy_class" in obj or "class_id" in obj or "is_mapped" in obj
            ):
                objects.append(
                    {
                        "original_class": obj.get("original_class"),
                        "easy_class": obj.get("easy_class"),
                        "class_id": obj.get("class_id"),
                        "is_mapped": obj.get("is_mapped", obj.get("easy_class") is not None),
                        "bbox_xyxy": bbox_xyxy,
                        "bbox_xywh": bbox_xywh,
                        "attributes": obj.get("attributes") or {},
                    }
                )
                continue

            objects.append(
                self._build_object(
                    original_class=original_class,
                    bbox_xyxy=bbox_xyxy,
                    bbox_xywh=bbox_xywh,
                    attributes=obj.get("attributes"),
                )
            )

        return self._build_record(
            image_path=image_path,
            source_annotation_path=annotation_path,
            objects=objects,
            width=item.get("width"),
            height=item.get("height"),
            split=item.get("split"),
            notes=item.get("notes"),
        )

    def _parse_csv_annotation(self, annotation_path):
        grouped = {}
        with annotation_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                image_reference = (
                    row.get("image_path")
                    or row.get("image_filename")
                    or row.get("image")
                    or row.get("file_name")
                )
                image_id = row.get("image_id") or (
                    Path(image_reference).stem if image_reference else None
                )
                key = image_reference or image_id
                grouped.setdefault(
                    key,
                    {
                        "image_reference": image_reference,
                        "image_id": image_id,
                        "width": row.get("width"),
                        "height": row.get("height"),
                        "split": row.get("split"),
                        "objects": [],
                    },
                )

                original_class = row.get("original_class") or row.get("class_name") or row.get("label")
                bbox_xyxy = None
                bbox_xywh = None
                if row.get("xmin") and row.get("ymin") and row.get("xmax") and row.get("ymax"):
                    bbox_xyxy = [
                        float(row["xmin"]),
                        float(row["ymin"]),
                        float(row["xmax"]),
                        float(row["ymax"]),
                    ]
                elif row.get("x") and row.get("y") and row.get("width") and row.get("height"):
                    bbox_xywh = [
                        float(row["x"]),
                        float(row["y"]),
                        float(row["width"]),
                        float(row["height"]),
                    ]
                grouped[key]["objects"].append(
                    self._build_object(original_class=original_class, bbox_xyxy=bbox_xyxy, bbox_xywh=bbox_xywh)
                )

        for grouped_item in grouped.values():
            image_path = self._find_image_path(
                image_reference=grouped_item["image_reference"],
                image_stem=grouped_item["image_id"],
            )
            if image_path is None:
                raise ValueError(
                    "Could not resolve image for CSV annotation '{}'".format(annotation_path)
                )
            yield self._build_record(
                image_path=image_path,
                source_annotation_path=annotation_path,
                objects=grouped_item["objects"],
                width=grouped_item["width"],
                height=grouped_item["height"],
                split=grouped_item["split"],
            )

    def _parse_voc_xml_annotation(self, annotation_path):
        tree = ET.parse(str(annotation_path))
        root = tree.getroot()
        image_reference = root.findtext("filename")
        image_path = self._find_image_path(
            image_reference=image_reference,
            image_stem=Path(image_reference).stem if image_reference else annotation_path.stem,
        )
        if image_path is None:
            raise ValueError(
                "Could not resolve image for VOC annotation '{}'".format(annotation_path)
            )

        size_node = root.find("size")
        width = size_node.findtext("width") if size_node is not None else None
        height = size_node.findtext("height") if size_node is not None else None

        objects = []
        for obj_node in root.findall("object"):
            original_class = obj_node.findtext("name")
            bbox_node = obj_node.find("bndbox")
            bbox_xyxy = None
            if bbox_node is not None:
                bbox_xyxy = [
                    float(bbox_node.findtext("xmin")),
                    float(bbox_node.findtext("ymin")),
                    float(bbox_node.findtext("xmax")),
                    float(bbox_node.findtext("ymax")),
                ]
            objects.append(self._build_object(original_class=original_class, bbox_xyxy=bbox_xyxy))

        yield self._build_record(
            image_path=image_path,
            source_annotation_path=annotation_path,
            objects=objects,
            width=width,
            height=height,
        )

    def _parse_annotation_file(self, annotation_path):
        suffix = annotation_path.suffix.lower()
        if suffix == ".json":
            for record in self._parse_json_annotation(annotation_path):
                yield record
        elif suffix == ".csv":
            for record in self._parse_csv_annotation(annotation_path):
                yield record
        elif suffix == ".xml":
            for record in self._parse_voc_xml_annotation(annotation_path):
                yield record
        else:
            raise ValueError(
                "Unsupported annotation format '{}' for {}".format(suffix, annotation_path)
            )

    def build_parse_manifest(self):
        layout = self.validate_staging_layout()
        scan = self.scan_staged_files()
        supported_formats = list(self.supported_annotation_suffixes)
        return {
            "dataset_key": self.dataset_key,
            "dataset_name": self.dataset_name,
            "modality": self.modality,
            "source_format": self.source_format,
            "thermal_only": self.thermal_only,
            "layout": layout,
            "scan": scan,
            "mapping_keys": sorted(self.schema["class_mapping"].get(self.dataset_key, {}).keys()),
            "supported_annotation_suffixes": supported_formats,
        }

    def simulate_parse(self):
        manifest = self.build_parse_manifest()
        readiness = "ready"
        if manifest["layout"]["errors"]:
            readiness = "blocked"
        elif manifest["layout"]["warnings"]:
            readiness = "partial"
        manifest["readiness"] = readiness
        return manifest

    @abstractmethod
    def iter_annotation_records(self):
        raise NotImplementedError
