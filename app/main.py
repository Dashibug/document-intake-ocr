from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Primary processing service for personal document images.",
    )

    app.include_router(router, prefix="/api/v1", tags=["documents"])

    app.mount(
        "/artifacts",
        StaticFiles(directory=str(settings.artifacts_dir)),
        name="artifacts",
    )

    return app


app = create_app()