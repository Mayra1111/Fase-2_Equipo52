"""
Health Check Router

Provides health check and status endpoints for API monitoring.
Includes API status, model load status, and system information.

Author: MLOps Team - Equipo 52
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from typing import Dict, Any

from src.api.schemas import HealthCheck
from src.api.dependencies import get_model_loader, ModelLoader
from src.api.config import settings
from src.utils.logger import setup_logger

# Setup router and logging
router = APIRouter(prefix="", tags=["Health"])
logger = setup_logger(__name__)


@router.get(
    "/health",
    response_model=HealthCheck,
    summary="Health Check",
    description="Check API and model status",
    responses={
        200: {"description": "API and model are healthy"},
        503: {"description": "Model not loaded or service unavailable"}
    }
)
async def health_check(loader: ModelLoader = Depends(get_model_loader)) -> HealthCheck:
    """
    Health check endpoint for API monitoring.

    Verifies that the API is running and the model is loaded.
    Used by load balancers and monitoring systems.

    Returns:
        HealthCheck: Status object containing health information

    Example:
        ```bash
        curl http://localhost:8000/health
        ```

        Response:
        ```json
        {
            "status": "healthy",
            "model_loaded": true,
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00.000000"
        }
        ```
    """
    try:
        # Use "healthy" if model loaded, "degraded" if not (not "unhealthy")
        status = "healthy" if loader.model_loaded else "degraded"

        health_check_response = HealthCheck(
            status=status,
            model_loaded=loader.model_loaded,
            version=settings.app_version,
            timestamp=datetime.utcnow().isoformat()
        )

        if status == "healthy":
            logger.debug("Health check passed")
        else:
            logger.warning("Health check failed: model not loaded")

        return health_check_response

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Health check failed"
        )


@router.get(
    "/status",
    summary="Extended Status",
    description="Get detailed API and model status",
    responses={
        200: {"description": "Status information retrieved successfully"}
    }
)
async def get_status(loader: ModelLoader = Depends(get_model_loader)) -> Dict[str, Any]:
    """
    Extended status endpoint with detailed information.

    Provides more detailed information about API and model status
    compared to the basic health check endpoint.

    Returns:
        dict: Extended status information

    Example:
        ```bash
        curl http://localhost:8000/status
        ```

        Response:
        ```json
        {
            "api_status": "online",
            "api_version": "1.0.0",
            "model_loaded": true,
            "model_name": "RandomForestClassifier",
            "model_version": "1.0.0",
            "features_required": 13,
            "timestamp": "2024-01-15T10:30:00.000000"
        }
        ```
    """
    try:
        model_status = loader.get_model_status()

        return {
            "api_status": "online",
            "api_version": settings.app_version,
            "api_name": settings.app_name,
            "model_loaded": model_status["model_loaded"],
            "model_name": model_status["model_name"],
            "model_version": model_status["model_version"],
            "features_required": settings.features_required,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve status"
        )


@router.get(
    "/",
    summary="API Root",
    description="Get API information and available endpoints",
    tags=["Info"]
)
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.

    Returns overview of the API, documentation links, and available endpoints.

    Returns:
        dict: API information and endpoint listing

    Example:
        ```bash
        curl http://localhost:8000/
        ```
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.description,
        "docs": settings.docs_url,
        "openapi": settings.openapi_url,
        "redoc": settings.redoc_url,
        "endpoints": {
            "health": "GET /health",
            "status": "GET /status",
            "model_info": "GET /model/info",
            "predict": "POST /predict",
            "predict_batch": "POST /predict/batch"
        }
    }
