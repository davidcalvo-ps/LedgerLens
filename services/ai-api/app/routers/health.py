from fastapi import APIRouter, Request

from app.config import SERVICE_NAME
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/v1/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
def live(request: Request) -> HealthResponse:
    """The process is up. Model providers are not contacted here."""
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=request.app.state.settings.version,
    )
