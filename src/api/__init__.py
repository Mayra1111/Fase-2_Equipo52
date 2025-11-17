"""
API module for Obesity Classification Model serving
"""

from .main import app
from .schemas import (
    ObesityFeatures,
    PredictionResponse,
    PredictionBatchRequest,
    PredictionBatchResponse,
    HealthCheck,
    ModelInfo,
    ErrorResponse
)

__all__ = [
    "app",
    "ObesityFeatures",
    "PredictionResponse",
    "PredictionBatchRequest",
    "PredictionBatchResponse",
    "HealthCheck",
    "ModelInfo",
    "ErrorResponse"
]
