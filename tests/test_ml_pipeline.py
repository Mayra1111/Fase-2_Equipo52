"""
Unit tests for ML pipeline
Validates training, evaluation, and model saving
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import joblib
import mlflow
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.models.data_preprocessor import DataPreprocessor
from src.models.model_trainer import ModelTrainer
from src.utils.config import REFACTORED_CLEAN_DATA_PATH, MODELS_DIR


class TestDataPreprocessor:
    """
    Test suite for DataPreprocessor
    """
    
    @pytest.fixture
    def df(self):
        """Load test data"""
        return pd.read_csv(REFACTORED_CLEAN_DATA_PATH)
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance"""
        return DataPreprocessor()
    
    def test_prepare_data(self, preprocessor, df):
        """Test data preparation"""
        X, y, mapping = preprocessor.prepare_data(df)
        
        assert X.shape[0] == df.shape[0], "Row count mismatch"
        assert X.shape[1] == df.shape[1], "Column count should include BMI"
        assert 'BMI' in X.columns, "BMI feature not created"
        assert len(y) == len(df), "Target length mismatch"
        assert isinstance(mapping, dict), "Mapping should be dictionary"
    
    def test_build_preprocessor(self, preprocessor, df):
        """Test preprocessor building"""
        X, y, _ = preprocessor.prepare_data(df)
        preproc = preprocessor.build_preprocessor(X)
        
        assert preproc is not None, "Preprocessor not built"
        assert preprocessor.num_cols is not None, "Numeric columns not identified"
        assert preprocessor.cat_cols is not None, "Categorical columns not identified"
    
    def test_target_encoding(self, preprocessor, df):
        """Test target encoding"""
        X, y, mapping = preprocessor.prepare_data(df)
        
        assert y.dtype in [np.int8, np.int32, np.int64], "Target not encoded to integers"
        assert preprocessor.clases_reales is not None, "Class names not stored"


class TestModelTrainer:
    """
    Test suite for ModelTrainer
    """
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_mlflow(self):
        """Setup MLflow for testing"""
        # Create temporary directory for MLflow runs
        self.temp_dir = tempfile.mkdtemp()
        mlflow.set_tracking_uri(f"file://{self.temp_dir}")
        
        # Create or get experiment
        experiment_name = "test_experiment"
        try:
            experiment_id = mlflow.create_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            # Experiment already exists
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
        
        mlflow.set_experiment(experiment_name)
        
        yield
        
        # Cleanup
        mlflow.end_run()  # End any active runs
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def setup_data(self):
        """Setup preprocessed data for training"""
        df = pd.read_csv(REFACTORED_CLEAN_DATA_PATH)
        preprocessor_obj = DataPreprocessor()
        X, y, mapping = preprocessor_obj.prepare_data(df)
        preproc = preprocessor_obj.build_preprocessor(X)
        target_names = preprocessor_obj.get_target_names()
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        return X_train, X_test, y_train, y_test, preproc, target_names
    
    def test_random_forest_training(self, setup_data):
        """Test RandomForest training"""
        X_train, X_test, y_train, y_test, preproc, target_names = setup_data
        
        trainer = ModelTrainer(preproc, target_names)
        model, predictions = trainer.train_random_forest(
            X_train, y_train, X_test, y_test
        )
        
        assert model is not None, "Model not trained"
        assert len(predictions) == len(y_test), "Predictions length mismatch"
        assert 'RandomForest' in trainer.models, "Model not stored"
        assert 'RandomForest' in trainer.predictions, "Predictions not stored"
    
    def test_get_best_model(self, setup_data):
        """Test best model selection"""
        X_train, X_test, y_train, y_test, preproc, target_names = setup_data
        
        trainer = ModelTrainer(preproc, target_names)
        trainer.train_random_forest(X_train, y_train, X_test, y_test)
        
        best_name, best_model, best_acc = trainer.get_best_model()
        
        assert best_name is not None, "Best model name not found"
        assert best_model is not None, "Best model not found"
        assert 0 <= best_acc <= 1, "Accuracy out of range"


class TestMLPipeline:
    """
    Test suite for complete ML pipeline
    """
    
    def test_pipeline_files_exist(self):
        """Test that required files exist"""
        assert REFACTORED_CLEAN_DATA_PATH.exists(), \
            f"Clean data not found: {REFACTORED_CLEAN_DATA_PATH}"
    
    def test_saved_model_exists(self):
        """Test that trained model exists"""
        model_path = MODELS_DIR / "best_pipeline.joblib"
        
        if model_path.exists():
            model = joblib.load(model_path)
            assert model is not None, "Model is None"
            assert hasattr(model, 'predict'), "Model doesn't have predict method"
        else:
            pytest.skip("Model not trained yet. Run: python scripts/run_ml.py")
    
    def test_saved_metadata_exists(self):
        """Test that model metadata exists"""
        metadata_path = MODELS_DIR / "model_metadata.joblib"
        
        if metadata_path.exists():
            metadata = joblib.load(metadata_path)
            assert 'model_name' in metadata, "Model name not in metadata"
            assert 'accuracy' in metadata, "Accuracy not in metadata"
            assert 'target_names' in metadata, "Target names not in metadata"
        else:
            pytest.skip("Metadata not saved yet. Run: python scripts/run_ml.py")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
