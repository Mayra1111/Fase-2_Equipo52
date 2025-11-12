"""
Router de Información del Modelo

Endpoints para obtener información sobre el modelo.
"""

from fastapi import APIRouter, Depends
import logging
from typing import Optional

from ..schemas import ModelInfo
from ..dependencies import get_metadata, get_model
from ..config import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/model",
    tags=["Model Info"]
)


@router.get(
    "/info",
    response_model=ModelInfo,
    summary="Información del Modelo",
    description="Retorna información detallada sobre el modelo en uso"
)
async def get_model_info(
    model = Depends(get_model),
    metadata: dict = Depends(get_metadata),
    settings: Settings = Depends(get_settings)
) -> ModelInfo:
    """
    Obtiene información detallada del modelo
    
    Args:
        model: Modelo cargado (inyectado)
        metadata: Metadata del modelo (inyectado)
        settings: Configuración del API (inyectado)
    
    Returns:
        ModelInfo: Información del modelo
    """
    # Extraer información del modelo
    classes = []
    if hasattr(model, 'classes_'):
        classes = [str(c) for c in model.classes_]
    
    # Extraer features del metadata o del modelo
    features = metadata.get('features', [])
    if not features and hasattr(model, 'feature_names_in_'):
        features = list(model.feature_names_in_)
    
    # Extraer métricas del metadata
    accuracy = metadata.get('best_accuracy', None)
    trained_date = metadata.get('training_date', None)
    
    logger.info(f"Retornando información del modelo: {settings.model_name} v{settings.model_version}")
    
    return ModelInfo(
        model_name=settings.model_name,
        model_version=settings.model_version,
        model_framework=settings.model_framework,
        accuracy=accuracy,
        classes=classes,
        features=features,
        trained_date=trained_date
    )


@router.get(
    "/version",
    summary="Versión del Modelo",
    description="Retorna la versión actual del modelo"
)
async def get_model_version(
    settings: Settings = Depends(get_settings)
) -> dict:
    """
    Obtiene la versión del modelo
    
    Args:
        settings: Configuración del API (inyectado)
    
    Returns:
        dict: Versión del modelo y del API
    """
    return {
        "model_name": settings.model_name,
        "model_version": settings.model_version,
        "api_version": settings.app_version,
        "model_path": settings.model_path
    }


@router.get(
    "/classes",
    summary="Clases del Modelo",
    description="Retorna las clases que el modelo puede predecir"
)
async def get_model_classes(
    model = Depends(get_model)
) -> dict:
    """
    Obtiene las clases que el modelo puede predecir
    
    Args:
        model: Modelo cargado (inyectado)
    
    Returns:
        dict: Lista de clases con sus descripciones
    """
    classes = []
    if hasattr(model, 'classes_'):
        classes = [str(c) for c in model.classes_]
    
    # Mapeo de clases a descripciones
    class_descriptions = {
        "Insufficient_Weight": "Peso Insuficiente",
        "Normal_Weight": "Peso Normal",
        "Overweight_Level_I": "Sobrepeso Nivel I",
        "Overweight_Level_II": "Sobrepeso Nivel II",
        "Obesity_Type_I": "Obesidad Tipo I",
        "Obesity_Type_II": "Obesidad Tipo II",
        "Obesity_Type_III": "Obesidad Tipo III"
    }
    
    return {
        "classes": classes,
        "total_classes": len(classes),
        "descriptions": {
            class_name: class_descriptions.get(class_name, class_name)
            for class_name in classes
        }
    }


@router.get(
    "/features",
    summary="Features del Modelo",
    description="Retorna las features que el modelo espera"
)
async def get_model_features(
    metadata: dict = Depends(get_metadata)
) -> dict:
    """
    Obtiene las features que el modelo espera
    
    Args:
        metadata: Metadata del modelo (inyectado)
    
    Returns:
        dict: Lista de features esperadas
    """
    features = metadata.get('features', [])
    
    # Descripción de features
    feature_descriptions = {
        "Gender": "Género (Male/Female)",
        "Age": "Edad en años",
        "Height": "Altura en metros",
        "Weight": "Peso en kilogramos",
        "family_history_with_overweight": "Historial familiar de sobrepeso (yes/no)",
        "FAVC": "Consumo frecuente de alimentos altos en calorías (yes/no)",
        "FCVC": "Frecuencia de consumo de vegetales (1-3)",
        "NCP": "Número de comidas principales (1-4)",
        "CAEC": "Consumo de alimentos entre comidas (no/Sometimes/Frequently/Always)",
        "SMOKE": "Fumador (yes/no)",
        "CH2O": "Consumo diario de agua en litros (1-3)",
        "SCC": "Monitorea consumo de calorías (yes/no)",
        "FAF": "Frecuencia de actividad física en días/semana (0-3)",
        "TUE": "Tiempo usando dispositivos tecnológicos en horas (0-2)",
        "CALC": "Consumo de alcohol (no/Sometimes/Frequently/Always)",
        "MTRANS": "Medio de transporte (Automobile/Motorbike/Bike/Public_Transportation/Walking)"
    }
    
    return {
        "features": features,
        "total_features": len(features),
        "descriptions": {
            feature: feature_descriptions.get(feature, "Sin descripción")
            for feature in features
        }
    }
