from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from contextlib import asynccontextmanager

from api.middleware import TimingMiddleware
from api.routes import channels, health, posts
from config.settings import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A scalable API for fetching the latest posts from various social media platforms",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(TimingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(posts.router, prefix=settings.API_V1_PREFIX)
app.include_router(channels.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - redirects to documentation"""
    return RedirectResponse(url=settings.DOCS_URL)


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": settings.DOCS_URL,
        "health_check": f"{settings.API_V1_PREFIX}/health",
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "docs": settings.DOCS_URL,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
