"""
FastAPI Application - Obesity Classification API

API de inferencia para el modelo de clasificación de obesidad.
Expone endpoints para realizar predicciones en tiempo real.

Autor: Equipo 52 - MLOps
Versión: 1.0.0
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .config import get_settings
from .dependencies import get_model_loader
from .routers import health, prediction, model_info

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para el ciclo de vida de la aplicación
    Carga el modelo al inicio
    """
    logger.info("=" * 80)
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("=" * 80)
    
    # Cargar modelo al inicio
    try:
        loader = get_model_loader()
        loader.load_model()
        loader.load_metadata()
        logger.info("✓ Modelo cargado exitosamente")
    except Exception as e:
        logger.error(f"✗ Error cargando modelo: {e}")
        raise
    
    logger.info(f"API lista en http://{settings.host}:{settings.port}")
    logger.info(f"Documentación disponible en http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 80)
    
    yield
    
    # Cleanup al cerrar
    logger.info("Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Equipo 52 - MLOps",
        "email": "equipo52@example.com"
    },
    license_info={
        "name": "MIT",
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para errores de validación"""
    logger.error(f"Error de validación: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Error en los datos de entrada",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para excepciones generales"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Error interno del servidor",
            "timestamp": datetime.now().isoformat()
        }
    )


# Incluir routers
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(model_info.router)


# Root endpoint
@app.get(
    "/",
    summary="Root",
    description="Endpoint raíz que retorna información básica del API",
    tags=["Root"]
)
async def root():
    """
    Endpoint raíz del API
    
    Returns:
        dict: Información básica del API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "model_version": settings.model_version,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "model_info": "/model/info",
            "model_version": "/model/version",
            "model_classes": "/model/classes",
            "model_features": "/model/features"
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
