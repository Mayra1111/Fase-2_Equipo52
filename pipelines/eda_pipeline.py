"""
EDA Pipeline for the Obesity ML Project
Orchestrates the complete EDA process with MLflow tracking
"""

import pandas as pd
import mlflow
from pathlib import Path
from typing import Optional

from src.data.data_loader import DataLoader
from src.data.data_cleaner import DataCleaner
from src.utils.config import (
    MODIFIED_DATA_PATH,
    REFACTORED_CLEAN_DATA_PATH,
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EDAPipeline:
    """
    Complete EDA pipeline with data loading, cleaning, and tracking
    """
    
    def __init__(
        self,
        input_path: Path = MODIFIED_DATA_PATH,
        output_path: Path = REFACTORED_CLEAN_DATA_PATH,
        use_mlflow: bool = True
    ):
        """
        Initialize EDA Pipeline
        
        Args:
            input_path: Path to input data (modified dataset)
            output_path: Path to save cleaned data
            use_mlflow: Whether to use MLflow tracking
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.use_mlflow = use_mlflow
        
        self.data_loader = None
        self.data_cleaner = None
        self.df_original = None
        self.df_cleaned = None
        
        logger.info("EDA Pipeline initialized")
        logger.info(f"Input: {self.input_path}")
        logger.info(f"Output: {self.output_path}")
    
    def run(self) -> pd.DataFrame:
        """
        Execute the complete EDA pipeline
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("="*70)
        logger.info("STARTING EDA PIPELINE")
        logger.info("="*70)
        
        # Setup MLflow if enabled
        if self.use_mlflow:
            self._setup_mlflow()
        
        try:
            with mlflow.start_run(run_name="eda_data_cleaning") if self.use_mlflow else self._no_op_context():
                # Step 1: Load data
                logger.info("\nSTEP 1: Loading data...")
                self.df_original = self._load_data()
                
                # Log input data info
                if self.use_mlflow:
                    mlflow.log_param("input_rows", self.df_original.shape[0])
                    mlflow.log_param("input_columns", self.df_original.shape[1])
                    mlflow.log_param("input_missing", self.df_original.isnull().sum().sum())
                
                # Step 2: Clean data
                logger.info("\nSTEP 2: Cleaning data...")
                self.df_cleaned = self._clean_data()
                
                # Log cleaning results
                if self.use_mlflow:
                    mlflow.log_param("output_rows", self.df_cleaned.shape[0])
                    mlflow.log_param("output_columns", self.df_cleaned.shape[1])
                    mlflow.log_param("output_missing", self.df_cleaned.isnull().sum().sum())
                    mlflow.log_metric("rows_preserved_pct", 
                                     (self.df_cleaned.shape[0] / self.df_original.shape[0]) * 100)
                
                # Step 3: Save cleaned data
                logger.info("\nSTEP 3: Saving cleaned data...")
                self._save_data()
                
                # Log artifact
                if self.use_mlflow:
                    mlflow.log_artifact(str(self.output_path))
                
                logger.info("="*70)
                logger.info("EDA PIPELINE COMPLETED SUCCESSFULLY")
                logger.info("="*70)
                logger.info(f"✓ Input shape: {self.df_original.shape}")
                logger.info(f"✓ Output shape: {self.df_cleaned.shape}")
                logger.info(f"✓ Output saved to: {self.output_path}")
                
                return self.df_cleaned
                
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def _setup_mlflow(self):
        """Setup MLflow tracking"""
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        logger.info(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
        logger.info(f"MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    
    def _load_data(self) -> pd.DataFrame:
        """Load data using DataLoader"""
        self.data_loader = DataLoader(self.input_path)
        df = self.data_loader.load_data()
        return df
    
    def _clean_data(self) -> pd.DataFrame:
        """Clean data using DataCleaner"""
        self.data_cleaner = DataCleaner()
        df_cleaned = self.data_cleaner.fit_transform(self.df_original)
        return df_cleaned
    
    def _save_data(self):
        """Save cleaned data to CSV"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.df_cleaned.to_csv(self.output_path, index=False, encoding='utf-8')
        logger.info(f"✓ Data saved to: {self.output_path}")
    
    def _no_op_context(self):
        """No-op context manager when MLflow is disabled"""
        from contextlib import contextmanager
        @contextmanager
        def dummy():
            yield
        return dummy()
    
    def get_summary(self) -> dict:
        """
        Get pipeline execution summary
        
        Returns:
            Dictionary with pipeline statistics
        """
        if self.df_cleaned is None:
            return {"error": "Pipeline not executed yet"}
        
        return {
            "input_shape": self.df_original.shape,
            "output_shape": self.df_cleaned.shape,
            "rows_preserved": self.df_cleaned.shape[0],
            "columns_final": self.df_cleaned.shape[1],
            "missing_values_removed": self.df_original.isnull().sum().sum() - self.df_cleaned.isnull().sum().sum(),
            "output_path": str(self.output_path)
        }


def run_eda_pipeline(
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    use_mlflow: bool = True
) -> pd.DataFrame:
    """
    Convenience function to run the EDA pipeline
    
    Args:
        input_path: Path to input data
        output_path: Path to save output data
        use_mlflow: Whether to use MLflow tracking
        
    Returns:
        Cleaned DataFrame
    """
    pipeline = EDAPipeline(
        input_path=input_path or MODIFIED_DATA_PATH,
        output_path=output_path or REFACTORED_CLEAN_DATA_PATH,
        use_mlflow=use_mlflow
    )
    
    df_cleaned = pipeline.run()
    summary = pipeline.get_summary()
    
    logger.info("\n" + "="*50)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*50)
    for key, value in summary.items():
        logger.info(f"{key}: {value}")
    
    return df_cleaned
