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
