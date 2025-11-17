"""
FastAPI Application - Obesity Classification API

Main application module that orchestrates:
- Router configuration and inclusion
- Middleware setup (CORS, error handling)
- Application lifecycle events (startup, shutdown)
- API documentation and metadata

Architecture:
- Lightweight orchestrator (this file)
- Modular routers (routers/ directory)
- Centralized dependencies (dependencies.py)
- Centralized configuration (config.py)
- Shared schemas (schemas.py)

This design allows independent extension of each router
without modifying the main application logic.

Author: MLOps Team - Equipo 52
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Import configuration
from src.api.config import settings

# Import routers
from src.api.routers import health_router, prediction_router, model_info_router

# Import dependencies
from src.api.dependencies import get_model_loader

# Import logger
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)


# ============================================================================
# FastAPI Application Initialization
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url
)

# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS Middleware - Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed error information.

    Returns:
        JSONResponse: Error response with validation details
    """
    logger.warning(f"Validation error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Returns:
        JSONResponse: Error response with timestamp
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Application Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event.

    Initializes:
    - Model loading
    - Logging setup
    - Configuration validation
    """
    logger.info("=" * 80)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 80)

    try:
        # Load model on startup
        loader = get_model_loader()
        loader.load_model()

        logger.info("✓ API startup complete")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"✗ API startup failed: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.

    Cleanup operations:
    - Log shutdown
    - Close connections if needed
    """
    logger.info("=" * 80)
    logger.info(f"Shutting down {settings.app_name}")
    logger.info("=" * 80)


# ============================================================================
# Router Registration
# ============================================================================

# Include health check router (includes root "/" endpoint)
app.include_router(
    health_router,
    tags=["Health", "Info"]
)

# Include prediction router
app.include_router(
    prediction_router,
    tags=["Prediction"]
)

# Include model information router
app.include_router(
    model_info_router,
    tags=["Model"]
)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting API server on {settings.host}:{settings.port}")
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
