from fastapi import APIRouter
from datetime import datetime, timezone

from api.dependencies import FetcherDep
from api.response_models.responses import HealthResponse
from config.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check(fetcher: FetcherDep):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION,
        available_platforms=fetcher.get_available_platforms(),
    )
