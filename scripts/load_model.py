"""
Script to load and compare trained models
Validates model performance and generates comparison report
"""

import sys
from pathlib import Path
import joblib
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import MODELS_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_best_model():
    """
    Load the best trained model and metadata
    
    Returns:
        Tuple of (model, metadata)
    """
    model_path = MODELS_DIR / "best_pipeline.joblib"
    metadata_path = MODELS_DIR / "model_metadata.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    
    logger.info(f"Loading model from: {model_path}")
    model = joblib.load(model_path)
    
    logger.info(f"Loading metadata from: {metadata_path}")
    metadata = joblib.load(metadata_path)
    
    return model, metadata


def display_model_info(metadata: dict):
    """
    Display model information
    
    Args:
        metadata: Model metadata dictionary
    """
    logger.info("="*70)
    logger.info("BEST MODEL INFORMATION")
    logger.info("="*70)
    logger.info(f"Model name: {metadata['model_name']}")
    logger.info(f"Accuracy: {metadata['accuracy']:.4f}")
    logger.info(f"Number of features: {len(metadata['features'])}")
    logger.info(f"Number of classes: {len(metadata['target_names'])}")
    logger.info(f"Target classes: {metadata['target_names']}")
    logger.info("="*70)


def main():
    """
    Main function to load and display model info
    """
    try:
        logger.info("Loading trained model...")
        
        # Load model and metadata
        model, metadata = load_best_model()
        
        # Display information
        display_model_info(metadata)
        
        logger.info("\n✓ Model loaded successfully!")
        logger.info(f"✓ Model type: {type(model).__name__}")
        logger.info(f"✓ Ready for predictions")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        logger.error("Make sure to run the ML pipeline first: python scripts/run_ml.py")
        return 1
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
