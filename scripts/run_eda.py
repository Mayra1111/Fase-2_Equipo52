"""
Main script to run the EDA pipeline
This script can be executed from the command line
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from pipelines.eda_pipeline import run_eda_pipeline
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main function to execute EDA pipeline
    """
    parser = argparse.ArgumentParser(description='Run EDA pipeline for Obesity dataset')
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input CSV file (default: data/raw/obesity_estimation_modified.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to output CSV file (default: data/interim/dataset_limpio_refactored.csv)'
    )
    parser.add_argument(
        '--no-mlflow',
        action='store_true',
        help='Disable MLflow tracking'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting EDA pipeline execution")
        
        # Run the pipeline
        df_cleaned = run_eda_pipeline(
            input_path=Path(args.input) if args.input else None,
            output_path=Path(args.output) if args.output else None,
            use_mlflow=not args.no_mlflow
        )
        
        logger.info(f"\n✓ Pipeline completed successfully!")
        logger.info(f"✓ Cleaned dataset shape: {df_cleaned.shape}")
        logger.info(f"✓ No missing values: {df_cleaned.isnull().sum().sum() == 0}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
