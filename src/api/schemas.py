"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ObesityFeatures(BaseModel):
    """
    Schema for obesity classification prediction input

    All numeric features should be float values
    Categorical features should be string values matching training data
    """
    Age: float = Field(..., ge=14, le=100, description="Age in years (14-100)")
    Height: float = Field(..., ge=1.0, le=2.5, description="Height in meters (1.0-2.5)")
    Weight: float = Field(..., ge=20, le=200, description="Weight in kg (20-200)")
    Gender: str = Field(..., description="Gender: 'Female' or 'Male'")

    # Nutritional features
    FCVC: float = Field(..., ge=1, le=3, description="Frequency of Consumption of Vegetables (1-3)")
    NCP: float = Field(..., ge=1, le=4, description="Number of Main Meals (1-4)")
    CAEC: str = Field(..., description="Consumption of Food Between Meals: 'no', 'Sometimes', 'Frequently', 'Always'")
    CH2O: float = Field(..., ge=1, le=3, description="Daily Water Consumption (1-3)")
    FAF: float = Field(..., ge=0, le=3, description="Frequency of Physical Activity (0-3)")

    # Lifestyle features
    TUE: float = Field(..., ge=0, le=2, description="Time Using Technology (0-2)")
    MTRANS: str = Field(..., description="Transportation: 'Walking', 'Bike', 'Motorbike', 'Public_Transportation', 'Automobile', 'Private_Car'")

    # Yes/No features
    family_history_with_overweight: str = Field(..., description="'yes' or 'no'")
    FAVC: str = Field(..., description="Frequent Consumption of High Caloric Food: 'yes' or 'no'")
    SCC: str = Field(..., description="Caloric Beverages Consumption: 'yes' or 'no'")

    class Config:
        schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    """
    Schema for prediction response
    """
    prediction: str = Field(..., description="Predicted obesity level")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")
    features_received: Dict[str, Any] = Field(..., description="Features received for prediction")
    model_name: str = Field(..., description="Name of the model used")
    model_version: str = Field(..., description="Version of the model")


class PredictionBatchRequest(BaseModel):
    """
    Schema for batch prediction requests
    """
    samples: List[ObesityFeatures] = Field(..., description="List of samples to predict")

    class Config:
        schema_extra = {
            "example": {
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
                    }
                ]
            }
        }


class PredictionBatchResponse(BaseModel):
    """
    Schema for batch prediction responses
    """
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    total_samples: int = Field(..., description="Total samples processed")
    successful: int = Field(..., description="Number of successful predictions")
    failed: int = Field(..., description="Number of failed predictions")


class HealthCheck(BaseModel):
    """
    Schema for health check response
    """
    status: str = Field(..., description="Status: 'healthy' or 'unhealthy'")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Timestamp of health check")


class ModelInfo(BaseModel):
    """
    Schema for model information endpoint
    """
    model_name: str = Field(..., description="Name of the model")
    model_version: str = Field(..., description="Version of the model")
    accuracy: float = Field(..., ge=0, le=1, description="Model accuracy on test set")
    classes: List[str] = Field(..., description="List of predicted classes")
    features_required: int = Field(..., description="Number of features required")
    deployment_date: str = Field(..., description="Date of deployment")


class ErrorResponse(BaseModel):
    """
    Schema for error responses
    """
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Timestamp of error")
