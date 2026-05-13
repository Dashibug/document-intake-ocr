from typing import Any, Literal

from pydantic import BaseModel, Field


class OCRItem(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[list[int]] | None = None


class ExtractedField(BaseModel):
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    source: str


class ArtifactLinks(BaseModel):
    input_image_url: str | None = None
    aligned_image_url: str | None = None
    annotated_image_url: str | None = None


class ProcessResponse(BaseModel):
    request_id: str
    document_type: str = "unknown"
    fields: dict[str, ExtractedField] = {}
    ocr: list[OCRItem] = []
    artifacts: ArtifactLinks
    warnings: list[str] = []


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    app_version: str
    device: str
    ocr_backend: str