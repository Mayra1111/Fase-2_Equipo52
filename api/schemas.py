"""
Schemas de datos para el API

Define los modelos Pydantic para validación de entrada/salida.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime


class ObesityInput(BaseModel):
    """
    Schema de entrada para predicción de obesidad
    
    Basado en el dataset de estimación de obesidad.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Gender": "Male",
                "Age": 25.0,
                "Height": 1.75,
                "Weight": 85.0,
                "family_history_with_overweight": "yes",
                "FAVC": "yes",
                "FCVC": 3.0,
                "NCP": 3.0,
                "CAEC": "Sometimes",
                "SMOKE": "no",
                "CH2O": 2.0,
                "SCC": "no",
                "FAF": 2.0,
                "TUE": 1.0,
                "CALC": "Sometimes",
                "MTRANS": "Public_Transportation"
            }
        }
    )
    
    # Datos demográficos
    Gender: Literal["Male", "Female"] = Field(
        ..., description="Género del individuo"
    )
    Age: float = Field(
        ..., ge=10, le=100, description="Edad en años"
    )
    Height: float = Field(
        ..., ge=1.0, le=2.5, description="Altura en metros"
    )
    Weight: float = Field(
        ..., ge=30, le=200, description="Peso en kilogramos"
    )
    
    # Historial familiar
    family_history_with_overweight: Literal["yes", "no"] = Field(
        ..., description="¿Tiene historial familiar de sobrepeso?"
    )
    
    # Hábitos alimenticios
    FAVC: Literal["yes", "no"] = Field(
        ..., description="¿Consume alimentos altos en calorías frecuentemente?"
    )
    FCVC: float = Field(
        ..., ge=1, le=3, description="Frecuencia de consumo de vegetales (1-3)"
    )
    NCP: float = Field(
        ..., ge=1, le=4, description="Número de comidas principales al día"
    )
    CAEC: Literal["no", "Sometimes", "Frequently", "Always"] = Field(
        ..., description="Consumo de alimentos entre comidas"
    )
    
    # Estilo de vida
    SMOKE: Literal["yes", "no"] = Field(
        ..., description="¿Fuma?"
    )
    CH2O: float = Field(
        ..., ge=1, le=3, description="Consumo diario de agua en litros (1-3)"
    )
    SCC: Literal["yes", "no"] = Field(
        ..., description="¿Monitorea el consumo de calorías?"
    )
    FAF: float = Field(
        ..., ge=0, le=3, description="Frecuencia de actividad física (días/semana, 0-3)"
    )
    TUE: float = Field(
        ..., ge=0, le=2, description="Tiempo usando dispositivos tecnológicos (horas, 0-2)"
    )
    CALC: Literal["no", "Sometimes", "Frequently", "Always"] = Field(
        ..., description="Consumo de alcohol"
    )
    MTRANS: Literal[
        "Automobile", "Motorbike", "Bike", "Public_Transportation", "Walking"
    ] = Field(
        ..., description="Medio de transporte usado frecuentemente"
    )


class ObesityPrediction(BaseModel):
    """
    Schema de salida para predicción de obesidad
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prediction": "Obesity_Type_I",
                "prediction_label": "Obesidad Tipo I",
                "confidence": 0.92,
                "probabilities": {
                    "Insufficient_Weight": 0.01,
                    "Normal_Weight": 0.02,
                    "Overweight_Level_I": 0.03,
                    "Overweight_Level_II": 0.02,
                    "Obesity_Type_I": 0.92,
                    "Obesity_Type_II": 0.00,
                    "Obesity_Type_III": 0.00
                },
                "bmi": 27.76,
                "timestamp": "2025-11-12T10:30:00",
                "model_version": "v1.0"
            }
        }
    )
    
    prediction: str = Field(
        ..., description="Clase predicha de obesidad"
    )
    prediction_label: str = Field(
        ..., description="Etiqueta legible de la predicción"
    )
    confidence: float = Field(
        ..., ge=0, le=1, description="Confianza de la predicción (0-1)"
    )
    probabilities: dict[str, float] = Field(
        ..., description="Probabilidades para todas las clases"
    )
    bmi: float = Field(
        ..., description="Índice de Masa Corporal calculado"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de la predicción"
    )
    model_version: str = Field(
        ..., description="Versión del modelo usado"
    )


class HealthResponse(BaseModel):
    """Schema para respuesta de health check"""
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del health check"
    )
    model_loaded: bool = Field(..., description="¿Modelo cargado correctamente?")
    version: str = Field(..., description="Versión del API")


class ModelInfo(BaseModel):
    """Schema para información del modelo"""
    model_name: str = Field(..., description="Nombre del modelo")
    model_version: str = Field(..., description="Versión del modelo")
    model_framework: str = Field(..., description="Framework usado")
    accuracy: Optional[float] = Field(None, description="Accuracy del modelo")
    classes: list[str] = Field(..., description="Clases que predice el modelo")
    features: list[str] = Field(..., description="Features que usa el modelo")
    trained_date: Optional[str] = Field(None, description="Fecha de entrenamiento")


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error detallado")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del error"
    )
