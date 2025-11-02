"""
Main script to run the ML pipeline for Obesity dataset
This script can be executed from the command line
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from pipelines.ml_pipeline import run_ml_pipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main function to execute ML pipeline
    """
    parser = argparse.ArgumentParser(description='Run ML pipeline for Obesity classification')
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input CSV file (default: data/interim/dataset_limpio_refactored.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Directory to save models (default: models/)'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        default='Clasificacion_Niveles_Obesidad',
        help='MLflow experiment name'
    )
    parser.add_argument(
        '--no-mlflow',
        action='store_true',
        help='Disable MLflow tracking'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting ML pipeline execution")
        
        # Run the pipeline
        results = run_ml_pipeline(
            input_path=Path(args.input) if args.input else None,
            output_dir=Path(args.output) if args.output else None,
            experiment_name=args.experiment,
            use_mlflow=not args.no_mlflow
        )
        
        logger.info(f"\n✓ Pipeline completed successfully!")
        logger.info(f"✓ Best model: {results['best_name']}")
        logger.info(f"✓ Best accuracy: {results['best_accuracy']:.4f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
