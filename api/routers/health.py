"""
Router de Health Check

Endpoints para verificar el estado del servicio.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ..schemas import HealthResponse
from ..dependencies import get_model_loader, ModelLoader
from ..config import get_settings, Settings

router = APIRouter(
    prefix="",
    tags=["Health"]
)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica que el servicio esté funcionando correctamente"
)
async def health_check(
    loader: ModelLoader = Depends(get_model_loader),
    settings: Settings = Depends(get_settings)
) -> HealthResponse:
    """
    Endpoint de health check básico
    
    Returns:
        HealthResponse: Estado del servicio
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        model_loaded=loader.is_loaded(),
        version=settings.app_version
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Readiness Check",
    description="Verifica que el servicio esté listo para recibir peticiones"
)
async def readiness_check(
    loader: ModelLoader = Depends(get_model_loader),
    settings: Settings = Depends(get_settings)
) -> HealthResponse:
    """
    Endpoint de readiness check - verifica que el modelo esté cargado
    
    Returns:
        HealthResponse: Estado de preparación del servicio
    
    Raises:
        500: Si el modelo no está cargado
    """
    # Intentar cargar el modelo si no está cargado
    if not loader.is_loaded():
        try:
            loader.load_model()
        except Exception as e:
            return HealthResponse(
                status="not_ready",
                timestamp=datetime.now(),
                model_loaded=False,
                version=settings.app_version
            )
    
    return HealthResponse(
        status="ready",
        timestamp=datetime.now(),
        model_loaded=True,
        version=settings.app_version
    )
