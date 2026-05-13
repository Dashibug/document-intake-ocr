from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.schemas import HealthResponse, ProcessResponse
from app.services.pipeline import DocumentProcessingPipeline
from app.utils.image import decode_image, safe_extension

router = APIRouter()

_pipeline: DocumentProcessingPipeline | None = None


def get_pipeline() -> DocumentProcessingPipeline:
    global _pipeline

    if _pipeline is None:
        _pipeline = DocumentProcessingPipeline()

    return _pipeline


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_version=settings.app_version,
        device=settings.device,
        ocr_backend=settings.ocr_backend,
    )


@router.post("/process", response_model=ProcessResponse)
async def process_document(
    file: UploadFile = File(...),
) -> ProcessResponse:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Expected image file, got content_type={file.content_type}",
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        image = decode_image(image_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extension = safe_extension(file.filename)

    pipeline = get_pipeline()

    return pipeline.process(
        image=image,
        original_filename=file.filename,
        original_bytes=image_bytes,
        extension=extension,
    )