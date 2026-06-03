"""
File utilities.

Helper functions for file operations.
"""

from pathlib import Path
from typing import List


def get_image_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get list of image files in directory.
    
    Args:
        directory: Path to directory
        recursive: Whether to search recursively
        
    Returns:
        List of image file paths
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    dir_path = Path(directory)
    
    pattern = '**/*' if recursive else '*'
    image_files = [
        str(f) for f in dir_path.glob(pattern)
        if f.suffix.lower() in image_extensions
    ]
    
    return sorted(image_files)


def get_label_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get list of label files in directory.
    
    Args:
        directory: Path to directory
        recursive: Whether to search recursively
        
    Returns:
        List of label file paths
    """
    dir_path = Path(directory)
    
    pattern = '**/*.txt' if recursive else '*.txt'
    label_files = [str(f) for f in dir_path.glob(pattern)]
    
    return sorted(label_files)


def create_dataset_symlinks(
    source_dir: str,
    target_dir: str,
    create_dirs: bool = True
) -> None:
    """
    Create symbolic links for dataset organization.
    
    Args:
        source_dir: Source dataset directory
        target_dir: Target directory for symlinks
        create_dirs: Whether to create target directories
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if create_dirs:
        target_path.mkdir(parents=True, exist_ok=True)
