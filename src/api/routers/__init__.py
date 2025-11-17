"""
API Routers

Modular endpoint definitions organized by functionality:
- health: Health check and status endpoints
- prediction: Model prediction endpoints (single and batch)
- model_info: Model metadata and information endpoints

Each router is independent and can be extended or replaced independently.
"""

from .health import router as health_router
from .prediction import router as prediction_router
from .model_info import router as model_info_router

__all__ = [
    "health_router",
    "prediction_router",
    "model_info_router",
]
