"""
API Configuration Settings

Centralized configuration for FastAPI application including
settings, API metadata, and model paths.

Author: MLOps Team - Equipo 52
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings and configuration

    These can be overridden by environment variables.
    Example: API_VERSION=2.0.0 python -m uvicorn src.api.main:app
    """

    # API Configuration
    app_name: str = Field("Obesity Classification API", description="API name")
    app_version: str = Field("1.0.0", description="API version")
    description: str = Field(
        "ML API for predicting obesity levels based on physical and nutritional features",
        description="API description"
    )

    # Model Configuration
    model_version: str = Field("1.0.0", description="Model version")
    deployment_date: str = Field("2024-01-15", description="Model deployment date")

    # Server Configuration
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    reload: bool = Field(False, description="Auto-reload on code changes")

    # CORS Configuration
    cors_origins: list = Field(["*"], description="CORS allowed origins")
    cors_credentials: bool = Field(True, description="Allow CORS credentials")
    cors_methods: list = Field(["*"], description="CORS allowed methods")
    cors_headers: list = Field(["*"], description="CORS allowed headers")

    # Logging Configuration
    log_level: str = Field("INFO", description="Logging level")

    # Feature Configuration
    features_required: int = Field(13, description="Number of required input features")

    # API Documentation
    docs_url: str = Field("/docs", description="Swagger UI URL")
    redoc_url: str = Field("/redoc", description="ReDoc URL")
    openapi_url: str = Field("/openapi.json", description="OpenAPI schema URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Get application settings

    Returns:
        Settings: Application configuration object
    """
    return Settings()


# Singleton instance
settings = get_settings()
