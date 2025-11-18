"""
Model evaluation script for Obesity classification
Evaluates trained models and generates evaluation metrics and visualizations
"""

import sys
import json
from pathlib import Path
import argparse
import joblib
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.models.model_evaluator import ModelEvaluator
from src.models.data_preprocessor import DataPreprocessor
from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    MODELS_DIR,
    METRICS_DIR,
    RANDOM_STATE
)
from src.utils.logger import setup_logger
from sklearn.model_selection import train_test_split

logger = setup_logger(__name__)


def main():
    """
    Main function to execute model evaluation
    """
    parser = argparse.ArgumentParser(
        description='Evaluate trained models for obesity classification'
    )
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to dataset (default: data/interim/dataset_limpio_refactored.csv)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Path to trained model (default: models/best_pipeline.joblib)'
    )
    parser.add_argument(
        '--metadata',
        type=str,
        default=None,
        help='Path to model metadata (default: models/model_metadata.joblib)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Directory to save evaluation results (default: reports/metrics/)'
    )

    args = parser.parse_args()

    # Set paths
    data_path = Path(args.data) if args.data else REFACTORED_CLEAN_DATA_PATH
    model_path = Path(args.model) if args.model else (MODELS_DIR / "best_pipeline.joblib")
    metadata_path = Path(args.metadata) if args.metadata else (MODELS_DIR / "model_metadata.joblib")
    output_dir = Path(args.output) if args.output else METRICS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("="*70)
        logger.info("STARTING MODEL EVALUATION")
        logger.info("="*70)
        logger.info(f"Data: {data_path}")
        logger.info(f"Model: {model_path}")
        logger.info(f"Output: {output_dir}")

        # Check if model exists
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        # Load data
        logger.info(f"\nLoading data from: {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Data loaded: {df.shape}")

        # Prepare data
        logger.info("\nPreparing data...")
        preprocessor = DataPreprocessor()
        X, y, _ = preprocessor.prepare_data(df, create_bmi=True)
        preprocessor.build_preprocessor(X)

        # Split data (same as training)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            stratify=y,
            random_state=RANDOM_STATE
        )

        logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

        # Load model
        logger.info(f"\nLoading model from: {model_path}")
        pipeline = joblib.load(model_path)

        # Load metadata
        logger.info(f"Loading metadata from: {metadata_path}")
        metadata = joblib.load(metadata_path)
        logger.info(f"Model name: {metadata['model_name']}")
        logger.info(f"Training accuracy: {metadata['accuracy']:.4f}")

        # Get predictions
        logger.info("\nGenerating predictions...")
        y_pred = pipeline.predict(X_test)
        y_pred_train = pipeline.predict(X_train)

        # Calculate metrics
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            confusion_matrix, classification_report
        )

        logger.info("="*70)
        logger.info("EVALUATION RESULTS ON TEST SET")
        logger.info("="*70)

        test_accuracy = accuracy_score(y_test, y_pred)
        test_precision = precision_score(y_test, y_pred, average='weighted')
        test_recall = recall_score(y_test, y_pred, average='weighted')
        test_f1 = f1_score(y_test, y_pred, average='weighted')

        train_accuracy = accuracy_score(y_train, y_pred_train)
        train_precision = precision_score(y_train, y_pred_train, average='weighted')
        train_recall = recall_score(y_train, y_pred_train, average='weighted')
        train_f1 = f1_score(y_train, y_pred_train, average='weighted')

        logger.info(f"\nTest Set Metrics:")
        logger.info(f"  Accuracy:  {test_accuracy:.4f}")
        logger.info(f"  Precision: {test_precision:.4f}")
        logger.info(f"  Recall:    {test_recall:.4f}")
        logger.info(f"  F1-Score:  {test_f1:.4f}")

        logger.info(f"\nTrain Set Metrics:")
        logger.info(f"  Accuracy:  {train_accuracy:.4f}")
        logger.info(f"  Precision: {train_precision:.4f}")
        logger.info(f"  Recall:    {train_recall:.4f}")
        logger.info(f"  F1-Score:  {train_f1:.4f}")

        # Overfitting analysis
        gap = train_accuracy - test_accuracy
        if gap > 0.1:
            status = "Overfitting detected"
        elif gap < -0.05:
            status = "Underfitting detected"
        else:
            status = "Good fit"

        logger.info(f"\nOverfitting Analysis:")
        logger.info(f"  Train-Test Gap: {gap:.4f}")
        logger.info(f"  Status: {status}")

        # Classification report
        target_names = metadata['target_names']
        logger.info(f"\nClassification Report:")
        report = classification_report(y_test, y_pred, target_names=target_names)
        logger.info(f"\n{report}")

        # Save metrics to JSON
        metrics_dict = {
            'model_name': metadata['model_name'],
            'test_accuracy': float(test_accuracy),
            'test_precision': float(test_precision),
            'test_recall': float(test_recall),
            'test_f1': float(test_f1),
            'train_accuracy': float(train_accuracy),
            'train_precision': float(train_precision),
            'train_recall': float(train_recall),
            'train_f1': float(train_f1),
            'train_test_gap': float(gap),
            'overfitting_status': status,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'target_names': target_names,
            'test_set_size': int(len(y_test)),
            'train_set_size': int(len(y_train))
        }

        metrics_file = output_dir / "evaluation_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics_dict, f, indent=4)
        logger.info(f"\n✓ Metrics saved to: {metrics_file}")

        # Create evaluation summary dataframe
        summary_df = pd.DataFrame({
            'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
            'Train': [train_accuracy, train_precision, train_recall, train_f1],
            'Test': [test_accuracy, test_precision, test_recall, test_f1]
        })

        summary_file = output_dir / "evaluation_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        logger.info(f"✓ Summary saved to: {summary_file}")

        logger.info("\n" + "="*70)
        logger.info("MODEL EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"✓ Test Accuracy: {test_accuracy:.4f}")
        logger.info(f"✓ Overfitting Status: {status}")
        logger.info(f"✓ Results saved to: {output_dir}")

        return 0

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
