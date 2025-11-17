"""
Dependency Injection for FastAPI

Provides model loading, caching, and dependency injection patterns
for the API application. Implements singleton pattern for model management.

Author: MLOps Team - Equipo 52
"""

from fastapi import HTTPException
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.utils.config import MODELS_DIR
from src.utils.logger import setup_logger
from src.api.config import settings

# Setup logging
logger = setup_logger(__name__)


class ModelLoader:
    """
    Singleton class for loading and caching the ML model and metadata.

    Ensures model is loaded only once and reused across API requests.
    Handles model loading errors gracefully.

    Attributes:
        _instance: Singleton instance
        model: Loaded ML model pipeline
        model_metadata: Model metadata dictionary
        model_loaded: Boolean flag indicating load status
    """

    _instance: Optional['ModelLoader'] = None

    def __new__(cls):
        """Ensure singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the model loader (called once due to singleton pattern)"""
        if self._initialized:
            return

        self.model = None
        self.model_metadata = None
        self.model_loaded = False
        self._initialized = True

    def load_model(self) -> None:
        """
        Load trained model from disk.

        Raises:
            FileNotFoundError: If model or metadata file not found
            Exception: If model loading fails

        Side Effects:
            Sets self.model, self.model_metadata, self.model_loaded
        """
        if self.model_loaded:
            logger.debug("Model already loaded, skipping reload")
            return

        try:
            model_path = MODELS_DIR / "best_pipeline.joblib"
            metadata_path = MODELS_DIR / "model_metadata.joblib"

            # Validate paths exist
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            if not metadata_path.exists():
                raise FileNotFoundError(f"Metadata not found at {metadata_path}")

            logger.info(f"Loading model from {model_path}")
            self.model = joblib.load(model_path)

            logger.info(f"Loading metadata from {metadata_path}")
            self.model_metadata = joblib.load(metadata_path)

            self.model_loaded = True
            logger.info(f"✓ Model loaded successfully: {self.model_metadata.get('model_name', 'Unknown')}")
            logger.info(f"✓ Model accuracy: {self.model_metadata.get('accuracy', 'Unknown'):.4f}")

        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            self.model_loaded = False
            raise

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            self.model_loaded = False
            raise

    def load_metadata(self) -> Dict[str, Any]:
        """
        Get model metadata without loading the model itself.

        Returns:
            dict: Model metadata dictionary

        Raises:
            HTTPException: If metadata cannot be loaded
        """
        if self.model_metadata is None:
            try:
                metadata_path = MODELS_DIR / "model_metadata.joblib"
                if not metadata_path.exists():
                    raise FileNotFoundError(f"Metadata not found at {metadata_path}")

                self.model_metadata = joblib.load(metadata_path)
            except Exception as e:
                logger.error(f"Failed to load metadata: {str(e)}")
                raise

        return self.model_metadata or {}

    def get_model_status(self) -> Dict[str, Any]:
        """
        Get current model load status.

        Returns:
            dict: Status information including model_loaded flag
        """
        return {
            "model_loaded": self.model_loaded,
            "model_name": self.model_metadata.get("model_name", "Unknown") if self.model_metadata else None,
            "model_version": settings.model_version
        }


# Global model loader instance
_model_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    """
    Get the singleton ModelLoader instance.

    This is the primary dependency injection point for the API.
    Used by routers to access the loaded model.

    Returns:
        ModelLoader: The singleton model loader instance

    Example:
        ```python
        from fastapi import Depends
        from src.api.dependencies import get_model_loader

        @app.get("/model/info")
        async def get_info(loader: ModelLoader = Depends(get_model_loader)):
            return loader.get_model_status()
        ```
    """
    global _model_loader

    if _model_loader is None:
        _model_loader = ModelLoader()

    return _model_loader


def get_loaded_model():
    """
    Dependency for getting the loaded model.

    Raises:
        HTTPException: If model is not loaded

    Returns:
        The loaded model object

    Example:
        ```python
        from fastapi import Depends

        @app.post("/predict")
        async def predict(features: Features, model = Depends(get_loaded_model)):
            return model.predict(...)
        ```
    """
    loader = get_model_loader()

    if not loader.model_loaded or loader.model is None:
        logger.error("Model not loaded - cannot process prediction")
        raise HTTPException(status_code=503, detail="Model not loaded. Try again later.")

    return loader.model


def get_model_metadata() -> Dict[str, Any]:
    """
    Dependency for getting model metadata.

    Raises:
        HTTPException: If metadata cannot be loaded

    Returns:
        dict: Model metadata dictionary

    Example:
        ```python
        from fastapi import Depends

        @app.get("/model/info")
        async def get_info(metadata: dict = Depends(get_model_metadata)):
            return metadata
        ```
    """
    loader = get_model_loader()

    try:
        return loader.load_metadata()
    except Exception as e:
        logger.error(f"Failed to get metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load model metadata")
