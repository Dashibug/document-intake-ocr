from pathlib import Path

import cv2
import numpy as np


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode uploaded image bytes into OpenCV BGR image."""
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image. Please upload a valid image file.")

    return image


def save_image(path: Path, image: np.ndarray) -> None:
    """Save OpenCV image to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)

    ok = cv2.imwrite(str(path), image)
    if not ok:
        raise RuntimeError(f"Failed to save image to {path}")


def safe_extension(filename: str | None) -> str:
    if not filename:
        return ".jpg"

    suffix = Path(filename).suffix.lower()

    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        return suffix

    return ".jpg"