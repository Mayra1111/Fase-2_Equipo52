"""
ML Pipeline for Obesity Classification
Orchestrates the complete ML workflow
"""

import pandas as pd
import numpy as np
import joblib
import mlflow
from pathlib import Path
from typing import Optional, Tuple
from sklearn.model_selection import train_test_split

from src.models.data_preprocessor import DataPreprocessor
from src.models.model_trainer import ModelTrainer
from src.models.model_evaluator import ModelEvaluator
from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    MODELS_DIR,
    MLFLOW_TRACKING_URI,
    RANDOM_STATE
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MLPipeline:
    """
    Complete ML pipeline for obesity classification
    """
    
    def __init__(
        self,
        input_path: Path = REFACTORED_CLEAN_DATA_PATH,
        output_dir: Path = MODELS_DIR,
        experiment_name: str = "Clasificacion_Niveles_Obesidad",
        random_state: int = RANDOM_STATE,
        use_mlflow: bool = True
    ):
        """
        Initialize ML Pipeline
        
        Args:
            input_path: Path to cleaned data
            output_dir: Directory to save models
            experiment_name: MLflow experiment name
            random_state: Random seed
            use_mlflow: Whether to use MLflow tracking
        """
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiment_name = experiment_name
        self.random_state = random_state
        self.use_mlflow = use_mlflow
        
        # Components
        self.preprocessor_obj = DataPreprocessor()
        self.trainer = None
        self.evaluator = None
        
        # Data
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.preprocessor = None
        self.target_names = None
        
        logger.info("ML Pipeline initialized")
        logger.info(f"Input: {self.input_path}")
        logger.info(f"Output: {self.output_dir}")
    
    def setup_mlflow(self):
        """Setup MLflow tracking"""
        if self.use_mlflow:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
            logger.info(f"MLflow experiment: {self.experiment_name}")
    
    def load_and_prepare_data(
        self,
        test_size: float = 0.2,
        create_bmi: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Load and prepare data for training
        
        Args:
            test_size: Fraction of data for testing
            create_bmi: Whether to create BMI feature
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info("="*70)
        logger.info("LOADING AND PREPARING DATA")
        logger.info("="*70)
        
        # Load data
        logger.info(f"Loading data from: {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        logger.info(f"Data loaded: {self.df.shape}")
        
        # Prepare data
        X, y, mapping = self.preprocessor_obj.prepare_data(self.df, create_bmi=create_bmi)
        
        # Build preprocessor
        self.preprocessor = self.preprocessor_obj.build_preprocessor(X)
        self.target_names = self.preprocessor_obj.get_target_names()
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=y,
            random_state=self.random_state
        )
        
        logger.info(f"Train: {self.X_train.shape}, Test: {self.X_test.shape}")
        logger.info(f"Train distribution:\n{pd.Series(self.y_train).value_counts()}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_all_models(self):
        """
        Train all models
        """
        logger.info("="*70)
        logger.info("TRAINING ALL MODELS")
        logger.info("="*70)
        
        self.trainer = ModelTrainer(
            self.preprocessor,
            self.target_names,
            self.random_state
        )
        
        # 1. RandomForest
        logger.info("\n1. Training RandomForest...")
        self.trainer.train_random_forest(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        
        # 2. XGBoost with SMOTE
        logger.info("\n2. Training XGBoost with SMOTE...")
        self.trainer.train_xgboost_smote(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        
        # 3. XGBoost simple
        logger.info("\n3. Training XGBoost (simple)...")
        self.trainer.train_xgboost_simple(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        
        # 4. KNN
        logger.info("\n4. Training KNN...")
        self.trainer.train_knn(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        
        # 5. SVM
        logger.info("\n5. Training SVM...")
        self.trainer.train_svm(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        
        logger.info("="*70)
        logger.info("ALL MODELS TRAINED")
        logger.info("="*70)
    
    def evaluate_models(self):
        """
        Evaluate and compare all models
        """
        logger.info("="*70)
        logger.info("EVALUATING MODELS")
        logger.info("="*70)
        
        self.evaluator = ModelEvaluator(
            self.trainer.models,
            self.trainer.predictions,
            self.y_test,
            self.preprocessor_obj.clases_reales.tolist()
        )
        
        # Create metrics dataframe
        metrics_df = self.evaluator.create_metrics_dataframe()
        logger.info("\nMetrics Comparison:")
        print(metrics_df.to_string(index=False))
        
        # Evaluate overfitting
        overfitting_df = self.evaluator.evaluate_overfitting(
            self.X_train, self.y_train,
            self.X_test, self.y_test
        )
        logger.info("\nOverfitting Analysis:")
        print(overfitting_df.to_string(index=False))
        
        # Generate all plots
        self.evaluator.generate_all_plots(metrics_df, overfitting_df)
        
        return metrics_df, overfitting_df
    
    def save_best_model(self) -> Tuple[str, float]:
        """
        Save the best model
        
        Returns:
            Best model name and accuracy
        """
        logger.info("="*70)
        logger.info("SAVING BEST MODEL")
        logger.info("="*70)
        
        best_name, best_model, best_acc = self.trainer.get_best_model()
        
        # Save model
        model_path = self.output_dir / "best_pipeline.joblib"
        joblib.dump(best_model, model_path)
        
        logger.info(f"Best model: {best_name}")
        logger.info(f"Accuracy: {best_acc:.4f}")
        logger.info(f"Model saved to: {model_path}")
        
        # Save metadata
        metadata = {
            'model_name': best_name,
            'accuracy': best_acc,
            'target_names': self.target_names,
            'features': self.X_train.columns.tolist(),
            'random_state': self.random_state
        }
        
        metadata_path = self.output_dir / "model_metadata.joblib"
        joblib.dump(metadata, metadata_path)
        logger.info(f"Metadata saved to: {metadata_path}")
        
        return best_name, best_acc
    
    def run(self):
        """
        Execute the complete ML pipeline
        """
        logger.info("="*70)
        logger.info("STARTING ML PIPELINE")
        logger.info("="*70)
        
        # Setup MLflow
        if self.use_mlflow:
            self.setup_mlflow()
        
        try:
            # 1. Load and prepare data
            self.load_and_prepare_data()
            
            # 2. Train all models
            self.train_all_models()
            
            # 3. Evaluate models
            metrics_df, overfitting_df = self.evaluate_models()
            
            # 4. Save best model
            best_name, best_acc = self.save_best_model()
            
            logger.info("="*70)
            logger.info("ML PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"✓ Best model: {best_name}")
            logger.info(f"✓ Best accuracy: {best_acc:.4f}")
            logger.info(f"✓ Models saved to: {self.output_dir}")
            
            return {
                'best_name': best_name,
                'best_accuracy': best_acc,
                'metrics': metrics_df,
                'overfitting': overfitting_df
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


def run_ml_pipeline(
    input_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    experiment_name: str = "Clasificacion_Niveles_Obesidad",
    use_mlflow: bool = True
) -> dict:
    """
    Convenience function to run the ML pipeline
    
    Args:
        input_path: Path to cleaned data
        output_dir: Directory to save models
        experiment_name: MLflow experiment name
        use_mlflow: Whether to use MLflow tracking
        
    Returns:
        Dictionary with results
    """
    pipeline = MLPipeline(
        input_path=input_path or REFACTORED_CLEAN_DATA_PATH,
        output_dir=output_dir or MODELS_DIR,
        experiment_name=experiment_name,
        use_mlflow=use_mlflow
    )
    
    results = pipeline.run()
    
    logger.info("\n" + "="*50)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*50)
    logger.info(f"Best model: {results['best_name']}")
    logger.info(f"Best accuracy: {results['best_accuracy']:.4f}")
    logger.info("="*50)
    
    return results
