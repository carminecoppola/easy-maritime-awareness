"""
YOLO dataset validation utilities.

Validate structure and format of YOLO datasets.
"""

from pathlib import Path
from typing import List, Dict, Tuple


def validate_yolo_dataset_structure(dataset_dir: str) -> Tuple[bool, List[str]]:
    """
    Validate YOLO dataset directory structure.
    
    Args:
        dataset_dir: Path to dataset directory
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    dataset_path = Path(dataset_dir)
    
    # Check required directories
    required_dirs = ['images', 'labels']
    for dir_name in required_dirs:
        if not (dataset_path / dir_name).exists():
            errors.append(f"Missing required directory: {dir_name}")
    
    # Check subdirectories
    required_subdirs = ['train', 'val', 'test']
    for subdir in required_subdirs:
        images_dir = dataset_path / 'images' / subdir
        labels_dir = dataset_path / 'labels' / subdir
        
        if not images_dir.exists():
            errors.append(f"Missing: images/{subdir}")
        if not labels_dir.exists():
            errors.append(f"Missing: labels/{subdir}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def count_classes_in_labels(labels_dir: str) -> Dict[int, int]:
    """
    Count occurrences of each class in label files.
    
    Args:
        labels_dir: Path to labels directory
        
    Returns:
        Dictionary with class IDs and their counts
    """
    class_counts = {}
    labels_path = Path(labels_dir)
    
    for label_file in labels_path.glob('*.txt'):
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    class_id = int(parts[0])
                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
    
    return class_counts
