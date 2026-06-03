"""
Image prediction utilities.

Run inference on single images.
"""

from pathlib import Path
from typing import List, Dict, Any


def predict_image(
    model_path: str,
    image_path: str,
    conf_threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Run inference on single image.
    
    Args:
        model_path: Path to trained model weights
        image_path: Path to input image
        conf_threshold: Confidence threshold for detections
        
    Returns:
        Dictionary with predictions
    """
    image_file = Path(image_path)
    
    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    predictions = {
        "image": str(image_file),
        "detections": [],
        "confidence_threshold": conf_threshold
    }
    
    return predictions
