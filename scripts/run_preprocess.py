"""
Data preprocessing and feature engineering script for Obesity classification
Prepares data for ML training by applying transformations and feature engineering
"""

import sys
import json
from pathlib import Path
import argparse
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.models.data_preprocessor import DataPreprocessor
from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    PROCESSED_DATA_DIR,
    RANDOM_STATE
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main function to execute preprocessing pipeline
    """
    parser = argparse.ArgumentParser(
        description='Preprocess data for obesity classification ML pipeline'
    )
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
        help='Directory to save preprocessed data (default: data/processed/)'
    )
    parser.add_argument(
        '--create-bmi',
        type=bool,
        default=True,
        help='Whether to create BMI feature (default: True)'
    )

    args = parser.parse_args()

    # Set paths
    input_path = Path(args.input) if args.input else REFACTORED_CLEAN_DATA_PATH
    output_dir = Path(args.output) if args.output else PROCESSED_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("="*70)
        logger.info("STARTING DATA PREPROCESSING")
        logger.info("="*70)
        logger.info(f"Input: {input_path}")
        logger.info(f"Output: {output_dir}")

        # Load data
        logger.info(f"\nLoading data from: {input_path}")
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        df = pd.read_csv(input_path)
        logger.info(f"Data loaded: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")

        # Initialize preprocessor
        preprocessor = DataPreprocessor()

        # Prepare data (encode target, create features)
        logger.info("\nPreparing data...")
        X, y, class_mapping = preprocessor.prepare_data(
            df,
            create_bmi=args.create_bmi
        )

        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        logger.info(f"Class mapping: {class_mapping}")

        # Build preprocessing pipeline (scaling, encoding)
        logger.info("\nBuilding preprocessing pipeline...")
        preprocessor.build_preprocessor(X)

        logger.info(f"Numeric columns: {preprocessor.num_cols}")
        logger.info(f"Categorical columns: {preprocessor.cat_cols}")

        # Combine features and target
        preprocessed_data = X.copy()
        preprocessed_data['target'] = y.values

        # Save preprocessed data
        output_file = output_dir / "dataset_preprocessed.csv"
        preprocessed_data.to_csv(output_file, index=False)
        logger.info(f"\nPreprocessed data saved: {output_file}")

        # Save metadata
        metadata = {
            'input_shape': df.shape,
            'output_shape': preprocessed_data.shape,
            'numeric_columns': preprocessor.num_cols,
            'categorical_columns': preprocessor.cat_cols,
            'class_mapping': class_mapping,
            'target_names': preprocessor.get_target_names(),
            'random_state': RANDOM_STATE,
            'bmi_created': args.create_bmi
        }

        metadata_file = output_dir / "preprocessing_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"Metadata saved: {metadata_file}")

        logger.info("="*70)
        logger.info("DATA PREPROCESSING COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"✓ Preprocessed dataset: {output_file}")
        logger.info(f"✓ Shape: {preprocessed_data.shape}")
        logger.info(f"✓ Target distribution:\n{pd.Series(y).value_counts()}")

        return 0

    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
