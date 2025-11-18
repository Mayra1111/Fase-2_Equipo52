"""
Prediction Router

Provides single and batch prediction endpoints.
Handles input validation, model inference, and response formatting.

Author: MLOps Team - Equipo 52
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError
import logging
import pandas as pd
import numpy as np
from typing import Any

from src.api.schemas import (
    ObesityFeatures,
    PredictionResponse,
    PredictionBatchRequest,
    PredictionBatchResponse
)
from src.api.dependencies import get_loaded_model, get_model_metadata, ModelLoader, get_model_loader
from src.api.config import settings
from src.utils.logger import setup_logger

# Setup router and logging
router = APIRouter(prefix="", tags=["Prediction"])
logger = setup_logger(__name__)


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Single Prediction",
    description="Make a single prediction for obesity classification",
    responses={
        200: {"description": "Prediction successful"},
        422: {"description": "Invalid input features"},
        503: {"description": "Model not loaded"}
    }
)
async def predict_single(
    features: ObesityFeatures,
    model = Depends(get_loaded_model),
    loader: ModelLoader = Depends(get_model_loader)
) -> PredictionResponse:
    """
    Make a single prediction for obesity classification.

    Takes obesity-related features as input and returns the predicted
    obesity level with associated metadata.

    Args:
        features (ObesityFeatures): Input features for prediction
        model: Injected loaded model (via dependency)
        loader: Injected model loader (via dependency)

    Returns:
        PredictionResponse: Prediction result with metadata

    Raises:
        HTTPException: If model is not loaded or prediction fails

    Example:
        ```bash
        curl -X POST http://localhost:8000/predict \
          -H "Content-Type: application/json" \
          -d '{
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
          }'
        ```

        Response:
        ```json
        {
            "prediction": "Overweight_Level_I",
            "confidence": null,
            "features_received": {...},
            "model_name": "RandomForestClassifier",
            "model_version": "1.0.0"
        }
        ```
    """
    try:
        # Convert features to dataframe
        features_dict = features.dict()
        features_df = pd.DataFrame([features_dict])

        # Calculate BMI feature (Weight / (Height/100)^2) if not already present
        if 'BMI' not in features_df.columns and 'Weight' in features_df.columns and 'Height' in features_df.columns:
            features_df['BMI'] = features_df['Weight'] / ((features_df['Height'] / 100) ** 2)
            logger.info(f"BMI calculated: {features_df['BMI'].values[0]:.2f}")

        logger.info(f"Processing single prediction with {len(features_df.columns)} features")

        # Make prediction with probability
        prediction_encoded = model.predict(features_df)[0]
        prediction_proba = model.predict_proba(features_df)[0]

        # Get class names from metadata
        target_names = loader.model_metadata.get("target_names", [])

        # Convert encoded prediction to class name
        if isinstance(prediction_encoded, (int, np.integer)):
            prediction_class = (
                target_names[int(prediction_encoded)]
                if prediction_encoded < len(target_names)
                else "Unknown"
            )
        else:
            prediction_class = str(prediction_encoded)

        # Get confidence score (max probability)
        confidence = float(np.max(prediction_proba)) if len(prediction_proba) > 0 else None

        logger.info(f"Prediction successful: {prediction_class} (confidence: {confidence:.4f})")

        return PredictionResponse(
            prediction=prediction_class,
            confidence=confidence,
            features_received=features_dict,
            model_name=loader.model_metadata.get("model_name", "Unknown"),
            model_version=settings.model_version
        )

    except ValidationError as e:
        logger.error(f"Validation error in prediction: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post(
    "/predict/batch",
    response_model=PredictionBatchResponse,
    summary="Batch Predictions",
    description="Make predictions for multiple samples",
    responses={
        200: {"description": "Batch predictions successful"},
        422: {"description": "Invalid input data"},
        503: {"description": "Model not loaded"}
    }
)
async def predict_batch(
    request: PredictionBatchRequest,
    model = Depends(get_loaded_model),
    loader: ModelLoader = Depends(get_model_loader)
) -> PredictionBatchResponse:
    """
    Make batch predictions for multiple samples.

    Takes a list of obesity feature sets and returns predictions
    for all samples with success/failure statistics.

    Args:
        request (PredictionBatchRequest): Batch of samples to predict
        model: Injected loaded model (via dependency)
        loader: Injected model loader (via dependency)

    Returns:
        PredictionBatchResponse: Batch predictions with statistics

    Raises:
        HTTPException: If input validation fails or prediction fails

    Example:
        ```bash
        curl -X POST http://localhost:8000/predict/batch \
          -H "Content-Type: application/json" \
          -d '{
            "samples": [
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
              },
              {...}
            ]
          }'
        ```

        Response:
        ```json
        {
            "predictions": [{...}, {...}],
            "total_samples": 2,
            "successful": 2,
            "failed": 0
        }
        ```
    """
    try:
        if not request.samples:
            raise ValueError("No samples provided")

        total_samples = len(request.samples)
        logger.info(f"Processing batch prediction for {total_samples} samples")

        # Convert all samples to dataframe
        samples_dicts = [sample.dict() for sample in request.samples]
        samples_df = pd.DataFrame(samples_dicts)

        # Calculate BMI feature (Weight / (Height/100)^2) if not already present
        if 'BMI' not in samples_df.columns and 'Weight' in samples_df.columns and 'Height' in samples_df.columns:
            samples_df['BMI'] = samples_df['Weight'] / ((samples_df['Height'] / 100) ** 2)
            logger.info(f"BMI calculated for {total_samples} samples")

        # Make batch predictions with probabilities
        predictions_encoded = model.predict(samples_df)
        predictions_proba = model.predict_proba(samples_df)

        # Get class names from metadata
        target_names = loader.model_metadata.get("target_names", [])

        # Convert predictions
        predictions = []
        successful = 0
        failed = 0

        for i, (pred_encoded, pred_probs, original_features) in enumerate(
            zip(predictions_encoded, predictions_proba, samples_dicts)
        ):
            try:
                # Convert encoded prediction to class name
                if isinstance(pred_encoded, (int, np.integer)):
                    pred_class = (
                        target_names[int(pred_encoded)]
                        if pred_encoded < len(target_names)
                        else "Unknown"
                    )
                else:
                    pred_class = str(pred_encoded)

                # Get confidence score (max probability)
                confidence = float(np.max(pred_probs)) if len(pred_probs) > 0 else None

                predictions.append(
                    PredictionResponse(
                        prediction=pred_class,
                        confidence=confidence,
                        features_received=original_features,
                        model_name=loader.model_metadata.get("model_name", "Unknown"),
                        model_version=settings.model_version
                    )
                )
                successful += 1

            except Exception as e:
                logger.warning(f"Failed to process sample {i}: {str(e)}")
                failed += 1

        logger.info(
            f"Batch prediction complete: {successful} successful, {failed} failed"
        )

        return PredictionBatchResponse(
            predictions=predictions,
            total_samples=total_samples,
            successful=successful,
            failed=failed
        )

    except ValueError as e:
        logger.error(f"Validation error in batch prediction: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )
