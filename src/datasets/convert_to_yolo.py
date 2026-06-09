"""
Format conversion utilities for YOLO format.
"""

from typing import List


def xyxy_to_yolo_line(class_id: int, bbox_xyxy: List[float], image_width: int, image_height: int) -> str:
    """
    Convert absolute XYXY bounding box coordinates to a YOLO annotation line.
    """
    x1, y1, x2, y2 = bbox_xyxy
    width = x2 - x1
    height = y2 - y1
    x_center = (x1 + width / 2.0) / float(image_width)
    y_center = (y1 + height / 2.0) / float(image_height)
    width_norm = width / float(image_width)
    height_norm = height / float(image_height)
    return "{} {:.6f} {:.6f} {:.6f} {:.6f}".format(
        int(class_id), x_center, y_center, width_norm, height_norm
    )


def intermediate_record_to_yolo_annotations(record: dict) -> List[str]:
    """
    Convert one intermediate-format record into YOLO annotation lines.
    Unmapped objects and objects without usable boxes are skipped.
    """
    lines = []
    image_width = record["width"]
    image_height = record["height"]
    for obj in record.get("objects", []):
        if not obj.get("is_mapped"):
            continue
        if obj.get("class_id") is None:
            continue
        bbox_xyxy = obj.get("bbox_xyxy")
        if bbox_xyxy is None and obj.get("bbox_xywh") is not None:
            x, y, width, height = obj["bbox_xywh"]
            bbox_xyxy = [x, y, x + width, y + height]
        if bbox_xyxy is None:
            continue
        lines.append(
            xyxy_to_yolo_line(
                class_id=obj["class_id"],
                bbox_xyxy=bbox_xyxy,
                image_width=image_width,
                image_height=image_height,
            )
        )
    return lines


def summarize_intermediate_to_yolo(records: List[dict]) -> dict:
    """
    Build a lightweight conversion summary from intermediate records.
    """
    image_count = len(records)
    annotation_count = 0
    for record in records:
        annotation_count += len(intermediate_record_to_yolo_annotations(record))
    return {
        "image_count": image_count,
        "annotation_count": annotation_count,
        "mode": "lightweight-summary",
    }
