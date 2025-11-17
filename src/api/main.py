"""
FastAPI service for Obesity Classification Model

Provides REST API endpoints for:
- Single and batch predictions
- Model information
- Health checks
- Performance monitoring

Author: MLOps Team - Equipo 52
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.api.schemas import (
    ObesityFeatures,
    PredictionResponse,
    PredictionBatchRequest,
    PredictionBatchResponse,
    HealthCheck,
    ModelInfo,
    ErrorResponse
)
from src.utils.config import MODELS_DIR
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# API Version
API_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"
DEPLOYMENT_DATE = "2024-01-15"

# Create FastAPI app
app = FastAPI(
    title="Obesity Classification API",
    description="ML API for predicting obesity levels based on physical and nutritional features",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and metadata
model = None
model_metadata = None
model_loaded = False


def load_model():
    """
    Load trained model and metadata from disk
    Called on startup
    """
    global model, model_metadata, model_loaded

    try:
        model_path = MODELS_DIR / "best_pipeline.joblib"
        metadata_path = MODELS_DIR / "model_metadata.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found at {metadata_path}")

        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)

        logger.info(f"Loading metadata from {metadata_path}")
        model_metadata = joblib.load(metadata_path)

        model_loaded = True
        logger.info(f"Model loaded successfully: {model_metadata.get('model_name', 'Unknown')}")
        logger.info(f"Model accuracy: {model_metadata.get('accuracy', 'Unknown'):.4f}")

    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        model_loaded = False
        raise


@app.on_event("startup")
async def startup_event():
    """
    Startup event - load model when API starts
    """
    logger.info("Starting Obesity Classification API...")
    try:
        load_model()
        logger.info("API startup complete")
    except Exception as e:
        logger.error(f"API startup failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event
    """
    logger.info("Shutting down Obesity Classification API...")


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthCheck: Status of the API and model
    """
    try:
        return HealthCheck(
            status="healthy" if model_loaded else "unhealthy",
            model_loaded=model_loaded,
            version=API_VERSION,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info():
    """
    Get information about the loaded model

    Returns:
        ModelInfo: Metadata about the model
    """
    if not model_loaded or model_metadata is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        return ModelInfo(
            model_name=model_metadata.get("model_name", "Unknown"),
            model_version=MODEL_VERSION,
            accuracy=float(model_metadata.get("accuracy", 0.0)),
            classes=model_metadata.get("target_names", []),
            features_required=13,  # Number of input features
            deployment_date=DEPLOYMENT_DATE
        )
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model info")


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_single(features: ObesityFeatures):
    """
    Make a single prediction for obesity classification

    Args:
        features: ObesityFeatures - Input features for prediction

    Returns:
        PredictionResponse: Predicted obesity level and metadata

    Example:
        ```json
        {
            "Age": 25.0,
            "Height": 1.75,
            "Weight": 85.0,
            "Gender": "Male",
            "FCVC": 2.0,
            "NCP": 3.0,
            "CAEC": "Sometimes",
            "CH2O": 2.5,
            "FAF": 1.5,
            "TUE": 1.0,
            "MTRANS": "Automobile",
            "family_history_with_overweight": "yes",
            "FAVC": "no",
            "SCC": "no"
        }
        ```
    """
    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Try again later.")

    try:
        # Convert features to dataframe
        features_dict = features.dict()
        features_df = pd.DataFrame([features_dict])

        logger.info(f"Making prediction for: {features_dict}")

        # Make prediction
        prediction_encoded = model.predict(features_df)[0]

        # Get class names from metadata
        target_names = model_metadata.get("target_names", [])

        # Convert encoded prediction to class name
        if isinstance(prediction_encoded, (int, np.integer)):
            prediction_class = target_names[int(prediction_encoded)] if prediction_encoded < len(target_names) else "Unknown"
        else:
            prediction_class = str(prediction_encoded)

        logger.info(f"Prediction result: {prediction_class}")

        return PredictionResponse(
            prediction=prediction_class,
            confidence=None,  # Could be enhanced with probability
            features_received=features_dict,
            model_name=model_metadata.get("model_name", "Unknown"),
            model_version=MODEL_VERSION
        )

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=PredictionBatchResponse, tags=["Prediction"])
async def predict_batch(request: PredictionBatchRequest):
    """
    Make batch predictions for multiple samples

    Args:
        request: PredictionBatchRequest - List of samples to predict

    Returns:
        PredictionBatchResponse: List of predictions with statistics
    """
    if not model_loaded or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Try again later.")

    try:
        if not request.samples:
            raise ValueError("No samples provided")

        total_samples = len(request.samples)
        logger.info(f"Processing batch prediction for {total_samples} samples")

        # Convert all samples to dataframe
        samples_dicts = [sample.dict() for sample in request.samples]
        samples_df = pd.DataFrame(samples_dicts)

        # Make batch predictions
        predictions_encoded = model.predict(samples_df)

        # Get class names from metadata
        target_names = model_metadata.get("target_names", [])

        # Convert predictions
        predictions = []
        successful = 0
        failed = 0

        for i, (pred_encoded, original_features) in enumerate(zip(predictions_encoded, samples_dicts)):
            try:
                # Convert encoded prediction to class name
                if isinstance(pred_encoded, (int, np.integer)):
                    pred_class = target_names[int(pred_encoded)] if pred_encoded < len(target_names) else "Unknown"
                else:
                    pred_class = str(pred_encoded)

                predictions.append(
                    PredictionResponse(
                        prediction=pred_class,
                        confidence=None,
                        features_received=original_features,
                        model_name=model_metadata.get("model_name", "Unknown"),
                        model_version=MODEL_VERSION
                    )
                )
                successful += 1

            except Exception as e:
                logger.warning(f"Failed to process sample {i}: {str(e)}")
                failed += 1

        logger.info(f"Batch prediction complete: {successful} successful, {failed} failed")

        return PredictionBatchResponse(
            predictions=predictions,
            total_samples=total_samples,
            successful=successful,
            failed=failed
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Obesity Classification API",
        "version": API_VERSION,
        "description": "ML API for predicting obesity levels",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "redoc": "/redoc",
        "endpoints": {
            "health": "GET /health",
            "model_info": "GET /model/info",
            "predict": "POST /predict",
            "predict_batch": "POST /predict/batch"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for all unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
