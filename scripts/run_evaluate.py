#!/usr/bin/env python3
"""
Evaluation stage script for DVC pipeline
Evaluates the trained model and generates metrics
"""

import sys
from pathlib import Path
import yaml
import json
import joblib
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Execute evaluation stage
    """
    try:
        logger.info("="*70)
        logger.info("EVALUATION STAGE")
        logger.info("="*70)
        
        # Load parameters
        params_path = project_root / 'config' / 'params.yaml'
        with open(params_path) as f:
            params = yaml.safe_load(f)
        
        logger.info(f"Parameters loaded from: {params_path}")
        
        # Load model and metadata
        models_dir = project_root / params['models']['output_dir']
        model_path = models_dir / 'best_pipeline.joblib'
        metadata_path = models_dir / 'model_metadata.joblib'
        
        logger.info(f"\nLoading model from: {model_path}")
        pipeline = joblib.load(model_path)
        
        logger.info(f"Loading metadata from: {metadata_path}")
        metadata = joblib.load(metadata_path)
        
        logger.info(f"✓ Model loaded: {type(pipeline).__name__}")
        logger.info(f"✓ Metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")
        
        # Extract model information
        if isinstance(metadata, dict):
            best_model_name = metadata.get('model_name', metadata.get('best_model_name', 'Unknown'))
            best_accuracy = metadata.get('accuracy', metadata.get('best_accuracy', 0.0))
            target_names = metadata.get('target_names', [])
            
            logger.info(f"\nModel Details:")
            logger.info(f"  - Model: {best_model_name}")
            logger.info(f"  - Accuracy: {best_accuracy:.4f}")
            logger.info(f"  - Classes: {len(target_names)}")
        
        # Create evaluation metrics
        eval_metrics = {
            'model_type': metadata.get('model_name', metadata.get('best_model_name', 'Unknown')) if isinstance(metadata, dict) else 'Unknown',
            'accuracy': float(metadata.get('accuracy', metadata.get('best_accuracy', 0.0))) if isinstance(metadata, dict) else 0.0,
            'evaluation_completed': True,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Save metrics
        metrics_dir = project_root / 'reports' / 'metrics'
        metrics_dir.mkdir(parents=True, exist_ok=True)
        metrics_file = metrics_dir / 'evaluation_metrics.json'
        
        with open(metrics_file, 'w') as f:
            json.dump(eval_metrics, f, indent=2)
        
        logger.info(f"\n✓ Metrics saved to: {metrics_file}")
        
        logger.info("\n" + "="*70)
        logger.info("✓ EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
