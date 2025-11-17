"""
Model Information Router

Provides endpoints for retrieving model metadata and information.
Includes model details, feature requirements, and performance metrics.

Author: MLOps Team - Equipo 52
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Dict, Any

from src.api.schemas import ModelInfo
from src.api.dependencies import get_model_metadata, ModelLoader, get_model_loader
from src.api.config import settings
from src.utils.logger import setup_logger

# Setup router and logging
router = APIRouter(prefix="/model", tags=["Model"])
logger = setup_logger(__name__)


@router.get(
    "/info",
    response_model=ModelInfo,
    summary="Model Information",
    description="Get detailed information about the loaded model",
    responses={
        200: {"description": "Model information retrieved successfully"},
        503: {"description": "Model not loaded"}
    }
)
async def get_model_info(
    loader: ModelLoader = Depends(get_model_loader)
) -> ModelInfo:
    """
    Get information about the loaded ML model.

    Returns metadata including model name, version, accuracy,
    predicted classes, and deployment information.

    Args:
        loader: Injected model loader (via dependency)

    Returns:
        ModelInfo: Model metadata and information

    Raises:
        HTTPException: If model is not loaded

    Example:
        ```bash
        curl http://localhost:8000/model/info
        ```

        Response:
        ```json
        {
            "model_name": "RandomForestClassifier",
            "model_version": "1.0.0",
            "accuracy": 0.92,
            "classes": [
                "Insufficient_Weight",
                "Normal_Weight",
                "Overweight_Level_I",
                "Overweight_Level_II",
                "Obesity_Type_I",
                "Obesity_Type_II",
                "Obesity_Type_III"
            ],
            "features_required": 13,
            "deployment_date": "2024-01-15"
        }
        ```
    """
    if not loader.model_loaded or loader.model_metadata is None:
        logger.error("Model not loaded - cannot retrieve info")
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    try:
        metadata = loader.model_metadata

        return ModelInfo(
            model_name=metadata.get("model_name", "Unknown"),
            model_version=settings.model_version,
            accuracy=float(metadata.get("accuracy", 0.0)),
            classes=metadata.get("target_names", []),
            features_required=settings.features_required,
            deployment_date=settings.deployment_date
        )

    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model information"
        )


@router.get(
    "/features",
    summary="Feature Requirements",
    description="Get list of required features for predictions",
    responses={
        200: {"description": "Feature list retrieved successfully"}
    }
)
async def get_required_features(
    loader: ModelLoader = Depends(get_model_loader)
) -> Dict[str, Any]:
    """
    Get list of required features for making predictions.

    Returns detailed information about all features required
    by the model for obesity classification.

    Args:
        loader: Injected model loader (via dependency)

    Returns:
        dict: Feature requirements and specifications

    Example:
        ```bash
        curl http://localhost:8000/model/features
        ```

        Response:
        ```json
        {
            "total_features": 13,
            "numeric_features": [
                "Age",
                "Height",
                "Weight",
                "FCVC",
                "NCP",
                "CH2O",
                "FAF",
                "TUE"
            ],
            "categorical_features": [
                "Gender",
                "CAEC",
                "MTRANS",
                "family_history_with_overweight",
                "FAVC",
                "SCC"
            ]
        }
        ```
    """
    return {
        "total_features": settings.features_required,
        "numeric_features": [
            "Age",
            "Height",
            "Weight",
            "FCVC",
            "NCP",
            "CH2O",
            "FAF",
            "TUE"
        ],
        "categorical_features": [
            "Gender",
            "CAEC",
            "MTRANS",
            "family_history_with_overweight",
            "FAVC",
            "SCC"
        ],
        "feature_descriptions": {
            "Age": "Age in years (14-100)",
            "Height": "Height in meters (1.0-2.5)",
            "Weight": "Weight in kg (20-200)",
            "Gender": "Gender: 'Female' or 'Male'",
            "FCVC": "Frequency of Consumption of Vegetables (1-3)",
            "NCP": "Number of Main Meals (1-4)",
            "CAEC": "Consumption of Food Between Meals: 'no', 'Sometimes', 'Frequently', 'Always'",
            "CH2O": "Daily Water Consumption (1-3)",
            "FAF": "Frequency of Physical Activity (0-3)",
            "TUE": "Time Using Technology (0-2)",
            "MTRANS": "Transportation: 'Walking', 'Bike', 'Motorbike', 'Public_Transportation', 'Automobile', 'Private_Car'",
            "family_history_with_overweight": "'yes' or 'no'",
            "FAVC": "Frequent Consumption of High Caloric Food: 'yes' or 'no'",
            "SCC": "Caloric Beverages Consumption: 'yes' or 'no'"
        }
    }


@router.get(
    "/classes",
    summary="Prediction Classes",
    description="Get list of obesity classifications the model can predict",
    responses={
        200: {"description": "Classes retrieved successfully"},
        503: {"description": "Model not loaded"}
    }
)
async def get_classes(
    loader: ModelLoader = Depends(get_model_loader)
) -> Dict[str, Any]:
    """
    Get list of obesity classification classes.

    Returns all possible prediction classes that the model
    can output for obesity classification.

    Args:
        loader: Injected model loader (via dependency)

    Returns:
        dict: Classification classes and descriptions

    Example:
        ```bash
        curl http://localhost:8000/model/classes
        ```

        Response:
        ```json
        {
            "classes": [
                "Insufficient_Weight",
                "Normal_Weight",
                "Overweight_Level_I",
                "Overweight_Level_II",
                "Obesity_Type_I",
                "Obesity_Type_II",
                "Obesity_Type_III"
            ],
            "total_classes": 7
        }
        ```
    """
    if not loader.model_loaded or loader.model_metadata is None:
        logger.error("Model not loaded - cannot retrieve classes")
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    try:
        target_names = loader.model_metadata.get("target_names", [])

        return {
            "classes": target_names,
            "total_classes": len(target_names)
        }

    except Exception as e:
        logger.error(f"Failed to get classes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve classification classes"
        )
