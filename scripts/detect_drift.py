"""
Main script for data drift detection
Compares baseline dataset with drifted dataset and generates comprehensive drift report
"""

import sys
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    INTERIM_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    NUMERIC_COLUMNS
)
from src.models.data_preprocessor import DataPreprocessor
from src.monitoring.drift_detector import DriftDetector
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_model_and_metadata():
    """
    Load trained model and metadata

    Returns:
        Tuple of (model, metadata)
    """
    model_path = MODELS_DIR / "best_pipeline.joblib"
    metadata_path = MODELS_DIR / "model_metadata.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}. Run ML pipeline first.")

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}. Run ML pipeline first.")

    logger.info(f"Loading model from: {model_path}")
    model = joblib.load(model_path)

    logger.info(f"Loading metadata from: {metadata_path}")
    metadata = joblib.load(metadata_path)

    return model, metadata


def evaluate_model_performance(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    dataset_name: str = "dataset"
) -> Dict[str, float]:
    """
    Evaluate model performance on a dataset

    Args:
        model: Trained model
        X: Features
        y: True labels
        dataset_name: Name for logging

    Returns:
        Dictionary with performance metrics
    """
    logger.info(f"Evaluating model on {dataset_name}...")

    # Make predictions
    y_pred = model.predict(X)

    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    metrics = {
        'accuracy': accuracy_score(y, y_pred),
        'precision': precision_score(y, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y, y_pred, average='weighted', zero_division=0)
    }

    logger.info(f"{dataset_name} metrics:")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {metrics['precision']:.4f}")
    logger.info(f"  Recall: {metrics['recall']:.4f}")
    logger.info(f"  F1-score: {metrics['f1']:.4f}")

    return metrics


def prepare_data_for_evaluation(
    df: pd.DataFrame,
    preprocessor: DataPreprocessor
) -> tuple:
    """
    Prepare data for model evaluation

    Args:
        df: Input DataFrame
        preprocessor: DataPreprocessor instance

    Returns:
        Tuple of (X, y) where X is features and y is target
    """
    # Prepare data (same as training)
    X, y, _ = preprocessor.prepare_data(df, create_bmi=True)

    # Build preprocessor (fit on this data for consistency)
    # Note: In production, you'd use the preprocessor from training
    preproc = preprocessor.build_preprocessor(X)

    return X, y


def main():
    """
    Main function for drift detection
    """
    logger.info("="*70)
    logger.info("DATA DRIFT DETECTION")
    logger.info("="*70)

    # Define paths
    baseline_path = REFACTORED_CLEAN_DATA_PATH
    drifted_path = INTERIM_DATA_DIR / "dataset_with_drift.csv"
    output_dir = REPORTS_DIR / "drift"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if files exist
    if not baseline_path.exists():
        logger.error(f"Baseline dataset not found: {baseline_path}")
        logger.error("Please run the EDA pipeline first: python scripts/run_eda.py")
        return 1

    if not drifted_path.exists():
        logger.error(f"Drifted dataset not found: {drifted_path}")
        logger.error("Please run drift simulation first: python scripts/simulate_drift.py")
        return 1

    try:
        # 1. Load datasets
        logger.info("\n1. Loading datasets...")
        df_baseline = pd.read_csv(baseline_path)
        df_drifted = pd.read_csv(drifted_path)

        logger.info(f"Baseline dataset: {df_baseline.shape}")
        logger.info(f"Drifted dataset: {df_drifted.shape}")

        # 2. Load model
        logger.info("\n2. Loading trained model...")
        model, metadata = load_model_and_metadata()
        logger.info(f"Model: {metadata['model_name']}")
        logger.info(f"Baseline accuracy: {metadata['accuracy']:.4f}")

        # 3. Prepare data preprocessor
        logger.info("\n3. Preparing data preprocessors...")
        preprocessor = DataPreprocessor()

        # Prepare baseline data
        X_baseline, y_baseline = prepare_data_for_evaluation(df_baseline, preprocessor)
        logger.info(f"Baseline features shape: {X_baseline.shape}")

        # Prepare drifted data
        X_drifted, y_drifted = prepare_data_for_evaluation(df_drifted, preprocessor)
        logger.info(f"Drifted features shape: {X_drifted.shape}")

        # 4. Evaluate model performance
        logger.info("\n4. Evaluating model performance...")
        baseline_metrics = evaluate_model_performance(
            model, X_baseline, y_baseline, "baseline"
        )

        current_metrics = evaluate_model_performance(
            model, X_drifted, y_drifted, "drifted"
        )

        # 5. Detect feature drift
        logger.info("\n5. Detecting feature drift...")
        detector = DriftDetector(
            psi_threshold=0.2,
            accuracy_degradation_threshold=0.05,
            accuracy_critical_threshold=0.10
        )

        # Use numeric columns for drift detection
        numeric_cols = [col for col in NUMERIC_COLUMNS if col in df_baseline.columns]

        drift_report = detector.detect_drift(
            baseline_data=df_baseline,
            current_data=df_drifted,
            baseline_metrics=baseline_metrics,
            current_metrics=current_metrics,
            numeric_columns=numeric_cols
        )

        # 6. Generate summary report
        logger.info("\n6. Generating drift report...")

        report_summary = {
            'baseline_dataset': str(baseline_path),
            'drifted_dataset': str(drifted_path),
            'model_name': metadata['model_name'],
            'baseline_metrics': baseline_metrics,
            'current_metrics': current_metrics,
            'performance_degradation': drift_report['performance_drift'],
            'feature_drift': drift_report['feature_drift'],  # Include full feature drift data
            'feature_drift_summary': {
                'total_features': drift_report['summary']['total_features_analyzed'],
                'features_with_drift': drift_report['summary']['features_with_drift'],
                'critical_alerts': drift_report['summary']['critical_alerts'],
                'warning_alerts': drift_report['summary']['warning_alerts']
            },
            'alerts': drift_report['alerts']
        }

        # Save JSON report
        report_path = output_dir / "drift_report.json"
        with open(report_path, 'w') as f:
            json.dump(report_summary, f, indent=2, default=str)
        logger.info(f"Report saved to: {report_path}")

        # Save alerts as text
        alerts_path = output_dir / "drift_alerts.txt"
        with open(alerts_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("DATA DRIFT ALERTS\n")
            f.write("="*70 + "\n\n")

            if not drift_report['alerts']:
                f.write("✓ No drift alerts detected.\n")
            else:
                for alert in drift_report['alerts']:
                    f.write(f"[{alert['level'].upper()}] {alert['type']}\n")
                    f.write(f"  {alert['message']}\n")
                    if 'psi' in alert:
                        f.write(f"  PSI: {alert['psi']:.3f}\n")
                    if 'degradation_pct' in alert:
                        f.write(f"  Degradation: {alert['degradation_pct']:.2f}%\n")
                    f.write("\n")

        logger.info(f"Alerts saved to: {alerts_path}")

        # 7. Print summary to console
        logger.info("\n" + "="*70)
        logger.info("DRIFT DETECTION SUMMARY")
        logger.info("="*70)
        logger.info(f"\nPerformance Comparison:")
        logger.info(f"  Baseline Accuracy: {baseline_metrics['accuracy']:.4f}")
        logger.info(f"  Current Accuracy: {current_metrics['accuracy']:.4f}")
        logger.info(f"  Degradation: {(baseline_metrics['accuracy'] - current_metrics['accuracy'])*100:.2f}%")

        logger.info(f"\nFeature Drift:")
        logger.info(f"  Features analyzed: {drift_report['summary']['total_features_analyzed']}")
        logger.info(f"  Features with drift: {drift_report['summary']['features_with_drift']}")

        logger.info(f"\nAlerts:")
        logger.info(f"  Critical: {drift_report['summary']['critical_alerts']}")
        logger.info(f"  Warnings: {drift_report['summary']['warning_alerts']}")

        if drift_report['alerts']:
            logger.info("\nTop Alerts:")
            for alert in drift_report['alerts'][:5]:  # Show top 5
                logger.info(f"  [{alert['level'].upper()}] {alert['message']}")

        logger.info("\n" + "="*70)
        logger.info("✓ Drift detection completed successfully!")
        logger.info(f"✓ Reports saved to: {output_dir}")
        logger.info("="*70)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Error in drift detection: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
