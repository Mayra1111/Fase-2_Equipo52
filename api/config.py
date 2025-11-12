"""
Configuración del servicio API

Este módulo contiene las configuraciones y settings del servicio FastAPI.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración del API"""
    
    # Información del API
    app_name: str = "Obesity Classification API"
    app_version: str = "1.0.0"
    app_description: str = "API para clasificación de obesidad usando XGBoost + SMOTE"
    
    # Paths
    model_path: str = "models/best_pipeline.joblib"
    metadata_path: str = "models/model_metadata.joblib"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: list = ["*"]
    
    # Model info
    model_name: str = "obesity_classifier"
    model_version: str = "v1.0"
    model_framework: str = "XGBoost + SMOTE"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retorna la instancia singleton de configuración"""
    return Settings()
