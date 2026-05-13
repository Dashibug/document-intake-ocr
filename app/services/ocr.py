from __future__ import annotations

from typing import Protocol

import numpy as np

from app.core.config import settings
from app.core.schemas import OCRItem


class OCRBackend(Protocol):
    def recognize(self, image: np.ndarray) -> tuple[list[OCRItem], list[str]]:
        ...


class StubOCR:
    def recognize(self, image: np.ndarray) -> tuple[list[OCRItem], list[str]]:
        return [], ["OCR is running in stub mode. No text was recognized."]


class EasyOCRBackend:
    """EasyOCR backend.

    EasyOCR returns:
    - bbox polygon
    - recognized text
    - confidence
    """

    def __init__(self) -> None:
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "EasyOCR is not installed. Install easyocr or set OCR_BACKEND=stub."
            ) from exc

        self.languages = self._parse_languages(settings.ocr_languages)
        self.use_gpu = self._should_use_gpu()

        settings.models_dir.mkdir(parents=True, exist_ok=True)

        self.reader = easyocr.Reader(
            self.languages,
            gpu=self.use_gpu,
            model_storage_directory=str(settings.models_dir),
            download_enabled=True,
            verbose=False,
        )

    def recognize(self, image: np.ndarray) -> tuple[list[OCRItem], list[str]]:
        warnings: list[str] = []

        if image is None or image.size == 0:
            return [], ["Empty image was passed to OCR backend."]

        try:

            rgb_image = image[:, :, ::-1]

            raw_result = self.reader.readtext(
                rgb_image,
                detail=1,
                paragraph=False,
            )

            items = self._parse_easyocr_result(raw_result)

            if not items:
                warnings.append("OCR finished successfully, but no text was detected.")

            warnings.append(
                f"EasyOCR backend used. languages={self.languages}, gpu={self.use_gpu}"
            )

            return items, warnings

        except Exception as exc:
            return [], [f"OCR failed with error: {type(exc).__name__}: {exc}"]

    def _parse_easyocr_result(self, raw_result: list) -> list[OCRItem]:
        items: list[OCRItem] = []

        for row in raw_result:
            try:
                bbox, text, confidence = row
            except Exception:
                continue

            normalized_bbox = [
                [int(point[0]), int(point[1])]
                for point in bbox
            ]

            items.append(
                OCRItem(
                    text=str(text),
                    confidence=max(0.0, min(1.0, float(confidence))),
                    bbox=normalized_bbox,
                )
            )

        return items

    def _parse_languages(self, value: str) -> list[str]:
        languages = [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

        return languages or ["en"]

    def _should_use_gpu(self) -> bool:
        device = settings.device.lower()

        if device == "cpu":
            return False

        if device == "gpu":
            return True

        if not settings.ocr_use_gpu_auto:
            return False

        try:
            import torch

            return bool(torch.cuda.is_available())
        except Exception:
            return False


class _FallbackOCRWithWarning:
    def __init__(self, warning: str) -> None:
        self.warning = warning

    def recognize(self, image: np.ndarray) -> tuple[list[OCRItem], list[str]]:
        return [], [self.warning]


def build_ocr_backend() -> OCRBackend:
    backend = settings.ocr_backend.lower()

    if backend == "stub":
        return StubOCR()

    if backend == "easyocr":
        try:
            return EasyOCRBackend()
        except Exception as exc:
            return _FallbackOCRWithWarning(
                f"EasyOCR backend failed to initialize. Stub OCR was used. Error: {exc}"
            )

    return _FallbackOCRWithWarning(
        f"Unknown OCR_BACKEND={settings.ocr_backend}. Stub OCR was used."
    )