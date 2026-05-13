from uuid import uuid4

import numpy as np

from app.core.config import settings
from app.core.schemas import ArtifactLinks, ProcessResponse
from app.services.alignment import DocumentAligner
from app.services.ocr import OCRBackend, build_ocr_backend
from app.services.visualization import Visualizer
from app.utils.image import save_image


class DocumentProcessingPipeline:
    def __init__(self) -> None:
        self.aligner = DocumentAligner()
        self.visualizer = Visualizer()
        self.ocr_backend: OCRBackend | None = None

    def _get_ocr_backend(self) -> OCRBackend:
        if self.ocr_backend is None:
            self.ocr_backend = build_ocr_backend()

        return self.ocr_backend

    def process(
        self,
        image: np.ndarray,
        original_filename: str | None = None,
        original_bytes: bytes | None = None,
        extension: str = ".jpg",
    ) -> ProcessResponse:
        request_id = uuid4().hex[:12]

        request_dir = settings.artifacts_dir / request_id
        request_dir.mkdir(parents=True, exist_ok=True)

        warnings: list[str] = []

        input_path = request_dir / f"input{extension}"
        aligned_path = request_dir / "aligned.jpg"
        annotated_path = request_dir / "annotated.jpg"

        # 1. Save original input image
        if settings.save_artifacts:
            if original_bytes is not None:
                input_path.write_bytes(original_bytes)
            else:
                save_image(input_path, image)

        # 2. Align document image
        try:
            aligned_image, alignment_warnings = self.aligner.align(image)
            warnings.extend(alignment_warnings)
        except Exception as exc:
            aligned_image = image.copy()
            warnings.append(
                f"Alignment failed with error: {type(exc).__name__}: {exc}. "
                "Original image was used as aligned image."
            )

        # 3. OCR
        try:
            ocr_backend = self._get_ocr_backend()
            ocr_items, ocr_warnings = ocr_backend.recognize(aligned_image)
            warnings.extend(ocr_warnings)
        except Exception as exc:
            ocr_items = []
            warnings.append(
                f"OCR failed with error: {type(exc).__name__}: {exc}"
            )

        # 4. Draw OCR boxes on aligned image
        try:
            annotated_image = self.visualizer.draw_ocr_annotations(
                image=aligned_image,
                request_id=request_id,
                ocr_items=ocr_items,
            )
        except Exception as exc:
            annotated_image = aligned_image.copy()
            warnings.append(
                f"Visualization failed with error: {type(exc).__name__}: {exc}. "
                "Aligned image was used as annotated image."
            )

        # 5. Save artifacts
        if settings.save_artifacts:
            save_image(aligned_path, aligned_image)
            save_image(annotated_path, annotated_image)

        artifacts = ArtifactLinks(
            input_image_url=f"/artifacts/{request_id}/{input_path.name}",
            aligned_image_url=f"/artifacts/{request_id}/{aligned_path.name}",
            annotated_image_url=f"/artifacts/{request_id}/{annotated_path.name}",
        )

        return ProcessResponse(
            request_id=request_id,
            document_type="unknown",
            fields={},
            ocr=ocr_items,
            artifacts=artifacts,
            warnings=warnings,
        )