"""
MassMIND staged parser.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from .base_parser import BaseDatasetParser


class MassMINDParser(BaseDatasetParser):
    dataset_key = "massmind"
    dataset_name = "MassMIND"
    modality = "thermal"
    source_format = "thermal-segmentation"
    thermal_only = True
    supported_annotation_suffixes = (".png", ".json", ".csv")

    semantic_label_names = {
        0: "Sky",
        1: "Water",
        2: "Bridge",
        3: "Obstacle",
        4: "Living Obstacle",
        5: "Background",
        6: "Self",
    }

    @property
    def semantic_dir(self):
        return self.annotations_dir / "semantic"

    @property
    def instance_dir(self):
        return self.annotations_dir / "instance"

    def expected_raw_structure(self):
        structure = super().expected_raw_structure()
        structure["required_directories"] = [
            str(self.images_dir),
            str(self.semantic_dir),
            str(self.instance_dir),
        ]
        return structure

    def _pair_paths(self):
        for instance_mask_path in sorted(self.instance_dir.glob("*.png")):
            stem = instance_mask_path.stem
            image_path = self.images_dir / "{}.png".format(stem)
            semantic_mask_path = self.semantic_dir / "{}.png".format(stem)
            if not image_path.exists():
                raise ValueError(
                    "Missing LWIR image for MassMIND instance mask '{}'".format(instance_mask_path)
                )
            if not semantic_mask_path.exists():
                raise ValueError(
                    "Missing semantic mask for MassMIND instance mask '{}'".format(instance_mask_path)
                )
            yield image_path, semantic_mask_path, instance_mask_path

    def _load_mask(self, mask_path):
        return np.array(Image.open(mask_path))

    def _instance_object(self, semantic_mask, instance_mask, instance_id):
        pixels = instance_mask == instance_id
        if not pixels.any():
            return None

        ys, xs = np.where(pixels)
        xmin = int(xs.min())
        ymin = int(ys.min())
        xmax = int(xs.max()) + 1
        ymax = int(ys.max()) + 1

        semantic_values = semantic_mask[pixels]
        unique_values, counts = np.unique(semantic_values, return_counts=True)
        semantic_label_id = int(unique_values[np.argmax(counts)])
        original_class = self.semantic_label_names.get(semantic_label_id, "Unknown")

        return self._build_object(
            original_class=original_class,
            bbox_xyxy=[xmin, ymin, xmax, ymax],
            attributes={
                "instance_id": int(instance_id),
                "semantic_label_id": semantic_label_id,
                "pixel_count": int(pixels.sum()),
            },
        )

    def iter_annotation_records(self):
        instance_masks = sorted(self.instance_dir.glob("*.png"))
        if instance_masks:
            for image_path, semantic_mask_path, instance_mask_path in self._pair_paths():
                semantic_mask = self._load_mask(semantic_mask_path)
                instance_mask = self._load_mask(instance_mask_path)

                objects = []
                for instance_id in sorted(int(value) for value in np.unique(instance_mask)):
                    if instance_id <= 0:
                        continue
                    obj = self._instance_object(semantic_mask, instance_mask, instance_id)
                    if obj is not None:
                        objects.append(obj)

                yield self._build_record(
                    image_path=image_path,
                    source_annotation_path=instance_mask_path,
                    objects=objects,
                    width=semantic_mask.shape[1],
                    height=semantic_mask.shape[0],
                    notes=[
                        "semantic_mask_path={}".format(semantic_mask_path),
                        "instance_mask_path={}".format(instance_mask_path),
                    ],
                )
            return

        for annotation_path in sorted(self.annotations_dir.rglob("*")):
            if not annotation_path.is_file():
                continue
            if annotation_path.suffix.lower() not in {".json", ".csv"}:
                continue
            for record in self._parse_annotation_file(annotation_path):
                yield record
