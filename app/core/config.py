from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Document Intake OCR"
    app_version: str = "0.1.0"

    artifacts_dir: Path = Path("artifacts")
    save_artifacts: bool = True

    models_dir: Path = Path("models")

    device: str = "auto"

    ocr_backend: str = "easyocr"
    ocr_languages: str = "en"
    ocr_use_gpu_auto: bool = True

    use_llm_extractor: bool = False
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()