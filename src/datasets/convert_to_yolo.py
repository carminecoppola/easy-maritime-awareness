"""
Format conversion utilities for YOLO format.

Convert various annotation formats to YOLO format.
"""

from pathlib import Path
from typing import List, Tuple


def coco_to_yolo(
    coco_annotations: List[dict],
    image_width: int,
    image_height: int
) -> List[str]:
    """
    Convert COCO format annotations to YOLO format.
    
    Args:
        coco_annotations: List of COCO annotation objects
        image_width: Width of image
        image_height: Height of image
        
    Returns:
        List of YOLO format annotations (one per line)
    """
    yolo_annotations = []
    
    for ann in coco_annotations:
        x, y, w, h = ann['bbox']
        # Convert to normalized center coordinates
        x_center = (x + w / 2) / image_width
        y_center = (y + h / 2) / image_height
        width_norm = w / image_width
        height_norm = h / image_height
        
        class_id = ann['category_id']
        yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}"
        yolo_annotations.append(yolo_line)
    
    return yolo_annotations


def validate_yolo_format(annotation_line: str) -> bool:
    """
    Validate YOLO annotation format.
    
    Args:
        annotation_line: Single YOLO format annotation line
        
    Returns:
        True if valid, False otherwise
    """
    parts = annotation_line.strip().split()
    if len(parts) != 5:
        return False
    
    try:
        class_id = int(parts[0])
        x_center, y_center, width, height = [float(p) for p in parts[1:]]
        
        # Check normalized coordinates are in [0, 1]
        if not all(0 <= v <= 1 for v in [x_center, y_center, width, height]):
            return False
            
        return True
    except ValueError:
        return False


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
