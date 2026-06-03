"""
Dataset inspection utilities.

Functions for analyzing dataset structure and statistics.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def count_images_by_source(raw_data_dir: str) -> Dict[str, int]:
    """
    Count image files by dataset source.
    
    Args:
        raw_data_dir: Path to raw data directory
        
    Returns:
        Dictionary with source names and image counts
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    counts = defaultdict(int)
    
    raw_path = Path(raw_data_dir)
    for source_dir in raw_path.iterdir():
        if source_dir.is_dir():
            for file in source_dir.rglob('*'):
                if file.suffix.lower() in image_extensions:
                    counts[source_dir.name] += 1
    
    return dict(counts)


def inspect_annotations(annotation_dir: str) -> Dict[str, int]:
    """
    Inspect annotation files structure.
    
    Args:
        annotation_dir: Path to annotation directory
        
    Returns:
        Dictionary with annotation file types and counts
    """
    annotation_types = defaultdict(int)
    
    anno_path = Path(annotation_dir)
    for file in anno_path.rglob('*'):
        if file.is_file():
            annotation_types[file.suffix] += 1
    
    return dict(annotation_types)
