from fastapi import FastAPI

from app.config import Settings, load_settings
from app.routers import health


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(
        title="LedgerLens AI API",
        version=settings.version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings
    app.include_router(health.router)
    return app


app = create_app()
