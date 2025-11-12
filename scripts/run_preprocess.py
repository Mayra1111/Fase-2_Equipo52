#!/usr/bin/env python3
"""
Preprocessing stage script for DVC pipeline
Prepares data for model training using MLPipeline
"""

import sys
from pathlib import Path
import yaml

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from pipelines.ml_pipeline import MLPipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Execute preprocessing stage
    """
    try:
        logger.info("="*70)
        logger.info("PREPROCESSING STAGE")
        logger.info("="*70)
        
        # Load parameters
        params_path = project_root / 'config' / 'params.yaml'
        with open(params_path) as f:
            params = yaml.safe_load(f)
        
        logger.info(f"Parameters loaded from: {params_path}")
        
        # Create pipeline instance
        pipeline = MLPipeline(
            input_path=params['data']['interim_path'],
            output_dir=params['models']['output_dir'],
            use_mlflow=False  # Disable MLflow for preprocessing stage
        )
        
        # Execute preprocessing
        logger.info("\nExecuting data preparation...")
        X_train, X_test, y_train, y_test = pipeline.load_and_prepare_data(
            test_size=params['data']['test_size'],
            create_bmi=params['preprocessing']['create_bmi']
        )
        
        logger.info("\n" + "="*70)
        logger.info("✓ PREPROCESSING COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"✓ Train set: {X_train.shape}")
        logger.info(f"✓ Test set: {X_test.shape}")
        logger.info(f"✓ Preprocessor built and ready for training")
        
        return 0
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
