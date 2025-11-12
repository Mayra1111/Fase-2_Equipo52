"""
Dependencias del API

Contiene funciones de dependencia reutilizables, incluyendo carga del modelo.
"""

import joblib
import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional

from .config import get_settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """Clase para manejar la carga y caché del modelo"""
    
    def __init__(self):
        self.model = None
        self.metadata = None
        self.settings = get_settings()
    
    def load_model(self):
        """Carga el modelo desde disco"""
        if self.model is None:
            try:
                model_path = Path(self.settings.model_path)
                if not model_path.exists():
                    raise FileNotFoundError(f"Modelo no encontrado en {model_path}")
                
                logger.info(f"Cargando modelo desde {model_path}")
                self.model = joblib.load(model_path)
                logger.info("Modelo cargado exitosamente")
                
            except Exception as e:
                logger.error(f"Error cargando modelo: {e}")
                raise
        
        return self.model
    
    def load_metadata(self) -> Optional[dict]:
        """Carga metadata del modelo si existe"""
        if self.metadata is None:
            try:
                metadata_path = Path(self.settings.metadata_path)
                if metadata_path.exists():
                    logger.info(f"Cargando metadata desde {metadata_path}")
                    self.metadata = joblib.load(metadata_path)
                    logger.info("Metadata cargada exitosamente")
                else:
                    logger.warning(f"Metadata no encontrada en {metadata_path}")
                    self.metadata = {}
            except Exception as e:
                logger.error(f"Error cargando metadata: {e}")
                self.metadata = {}
        
        return self.metadata
    
    def is_loaded(self) -> bool:
        """Verifica si el modelo está cargado"""
        return self.model is not None


# Instancia global del loader
_model_loader = ModelLoader()


@lru_cache()
def get_model_loader() -> ModelLoader:
    """
    Dependency para obtener el model loader
    
    Returns:
        ModelLoader: Instancia del loader de modelo
    """
    return _model_loader


def get_model():
    """
    Dependency para obtener el modelo cargado
    
    Returns:
        Model: Pipeline del modelo entrenado
    
    Raises:
        RuntimeError: Si el modelo no se puede cargar
    """
    loader = get_model_loader()
    return loader.load_model()


def get_metadata() -> dict:
    """
    Dependency para obtener metadata del modelo
    
    Returns:
        dict: Metadata del modelo
    """
    loader = get_model_loader()
    return loader.load_metadata()


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calcula el Índice de Masa Corporal (BMI)
    
    Args:
        weight: Peso en kilogramos
        height: Altura en metros
    
    Returns:
        float: BMI calculado
    """
    return round(weight / (height ** 2), 2)


def get_obesity_label(prediction: str) -> str:
    """
    Convierte el código de predicción a una etiqueta legible
    
    Args:
        prediction: Código de la predicción
    
    Returns:
        str: Etiqueta legible en español
    """
    labels = {
        "Insufficient_Weight": "Peso Insuficiente",
        "Normal_Weight": "Peso Normal",
        "Overweight_Level_I": "Sobrepeso Nivel I",
        "Overweight_Level_II": "Sobrepeso Nivel II",
        "Obesity_Type_I": "Obesidad Tipo I",
        "Obesity_Type_II": "Obesidad Tipo II",
        "Obesity_Type_III": "Obesidad Tipo III"
    }
    return labels.get(prediction, prediction)
