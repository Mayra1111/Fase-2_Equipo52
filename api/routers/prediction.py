"""
Router de Predicción

Endpoints para realizar predicciones de obesidad.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging
import numpy as np
import pandas as pd

from ..schemas import ObesityInput, ObesityPrediction, ErrorResponse
from ..dependencies import (
    get_model, 
    get_metadata, 
    calculate_bmi, 
    get_obesity_label
)
from ..config import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post(
    "",
    response_model=ObesityPrediction,
    summary="Predecir Obesidad",
    description="Realiza una predicción de obesidad basada en los datos de entrada",
    responses={
        200: {
            "description": "Predicción exitosa",
            "model": ObesityPrediction
        },
        400: {
            "description": "Error en los datos de entrada",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def predict_obesity(
    input_data: ObesityInput,
    model = Depends(get_model),
    metadata: dict = Depends(get_metadata),
    settings: Settings = Depends(get_settings)
) -> ObesityPrediction:
    """
    Realiza una predicción de obesidad
    
    Args:
        input_data: Datos del individuo para predicción
        model: Modelo cargado (inyectado)
        metadata: Metadata del modelo (inyectado)
        settings: Configuración del API (inyectado)
    
    Returns:
        ObesityPrediction: Resultado de la predicción con probabilidades
    
    Raises:
        HTTPException: Si hay un error durante la predicción
    """
    try:
        # Convertir input a DataFrame
        input_dict = input_data.model_dump()
        
        # Calcular BMI y agregarlo al input
        bmi_value = calculate_bmi(input_data.Weight, input_data.Height)
        input_dict['BMI'] = bmi_value
        
        df = pd.DataFrame([input_dict])
        
        logger.info(f"Realizando predicción con input (BMI={bmi_value}): {input_dict}")
        
        # Realizar predicción
        prediction = model.predict(df)[0]
        
        # Obtener probabilidades si el modelo lo soporta
        try:
            probabilities = model.predict_proba(df)[0]
            
            # Obtener las clases del modelo - primero intentar desde metadata
            classes = metadata.get('target_names', [])
            
            # Si no hay en metadata, intentar del modelo
            if not classes and hasattr(model, 'classes_'):
                classes = model.classes_
            
            # Crear diccionario de probabilidades
            prob_dict = {}
            if len(classes) > 0:
                prob_dict = {
                    str(class_name): float(prob) 
                    for class_name, prob in zip(classes, probabilities)
                }
            else:
                # Si no hay clases, usar nombres genéricos
                prob_dict = {
                    f"class_{i}": float(prob) 
                    for i, prob in enumerate(probabilities)
                }
            
            # Confianza es la probabilidad de la clase predicha
            confidence = float(max(probabilities))
            
            # Si la predicción es numérica, mapearla al nombre de clase
            if isinstance(prediction, (int, np.integer)) and len(classes) > 0:
                prediction = classes[prediction]
            
        except Exception as e:
            logger.warning(f"No se pudieron obtener probabilidades: {e}")
            prob_dict = {str(prediction): 1.0}
            confidence = 1.0
        
        # BMI ya fue calculado al inicio
        # bmi_value ya contiene el valor calculado
        
        # Obtener etiqueta legible
        prediction_label = get_obesity_label(str(prediction))
        
        logger.info(f"Predicción exitosa: {prediction} (confianza: {confidence:.2f})")
        
        return ObesityPrediction(
            prediction=str(prediction),
            prediction_label=prediction_label,
            confidence=confidence,
            probabilities=prob_dict,
            bmi=bmi_value,  # Usar el BMI ya calculado
            timestamp=datetime.now(),
            model_version=settings.model_version
        )
        
    except ValueError as e:
        logger.error(f"Error de validación en predicción: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ValidationError",
                "message": f"Error en los datos de entrada: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"Error inesperado en predicción: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PredictionError",
                "message": f"Error al realizar la predicción: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.post(
    "/batch",
    summary="Predicción por Lote",
    description="Realiza predicciones para múltiples individuos",
    response_model=list[ObesityPrediction],
    responses={
        200: {
            "description": "Predicciones exitosas",
        },
        400: {
            "description": "Error en los datos de entrada",
            "model": ErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": ErrorResponse
        }
    }
)
async def predict_obesity_batch(
    input_data: list[ObesityInput],
    model = Depends(get_model),
    metadata: dict = Depends(get_metadata),
    settings: Settings = Depends(get_settings)
) -> list[ObesityPrediction]:
    """
    Realiza predicciones para múltiples individuos
    
    Args:
        input_data: Lista de datos de individuos
        model: Modelo cargado (inyectado)
        metadata: Metadata del modelo (inyectado)
        settings: Configuración del API (inyectado)
    
    Returns:
        list[ObesityPrediction]: Lista de predicciones
    
    Raises:
        HTTPException: Si hay un error durante las predicciones
    """
    try:
        predictions = []
        
        for idx, data in enumerate(input_data):
            logger.info(f"Procesando predicción {idx + 1}/{len(input_data)}")
            
            # Reutilizar la función de predicción individual
            prediction = await predict_obesity(data, model, metadata, settings)
            predictions.append(prediction)
        
        logger.info(f"Predicciones batch completadas: {len(predictions)} predicciones")
        return predictions
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    
    except Exception as e:
        logger.error(f"Error en predicción batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "BatchPredictionError",
                "message": f"Error al realizar predicciones batch: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )
