"""
Data preprocessing module for ML pipeline
Handles feature engineering and preprocessing
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataPreprocessor:
    """
    Preprocessor for ML features
    """
    
    def __init__(self, target_col: str = 'NObeyesdad'):
        """
        Initialize DataPreprocessor
        
        Args:
            target_col: Name of target column
        """
        self.target_col = target_col
        self.preprocessor = None
        self.clases_reales = None
        self.mapping_names = None
        self.num_cols = None
        self.cat_cols = None
        
        logger.info("DataPreprocessor initialized")
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        create_bmi: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series, dict]:
        """
        Prepare data for ML: encode target, create features
        
        Args:
            df: Input DataFrame
            create_bmi: Whether to create BMI feature
            
        Returns:
            X (features), y (target), class_mapping
        """
        logger.info("Preparing data for ML...")
        
        df_copy = df.copy()
        
        # Encode target if categorical
        if df_copy[self.target_col].dtype == 'object':
            df_copy[self.target_col] = df_copy[self.target_col].astype('category')
            self.clases_reales = df_copy[self.target_col].cat.categories
            df_copy[self.target_col] = df_copy[self.target_col].cat.codes
            
            logger.info(f"Target encoded. Classes: {df_copy[self.target_col].unique()}")
            logger.info(f"Class names: {self.clases_reales.tolist()}")
        
        # Create mapping for display
        self.mapping_names = {
            i: f"{i}-{name}" for i, name in enumerate(self.clases_reales)
        }
        
        # Feature engineering: create BMI
        if create_bmi and {'Height', 'Weight'}.issubset(df_copy.columns):
            df_copy['BMI'] = df_copy['Weight'] / ((df_copy['Height'] / 100) ** 2)
            logger.info("BMI feature created")
        
        # Separate features and target
        X = df_copy.drop(columns=[self.target_col])
        y = df_copy[self.target_col]
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target distribution:\n{pd.Series(y).value_counts()}")
        
        return X, y, self.mapping_names
    
    def build_preprocessor(self, X: pd.DataFrame) -> ColumnTransformer:
        """
        Build preprocessing pipeline
        
        Args:
            X: Feature DataFrame
            
        Returns:
            ColumnTransformer for preprocessing
        """
        logger.info("Building preprocessing pipeline...")
        
        # Identify numeric and categorical columns
        self.num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        self.cat_cols = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        logger.info(f"Numeric columns: {self.num_cols}")
        logger.info(f"Categorical columns: {self.cat_cols}")
        
        # Numeric pipeline
        num_pipe = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical pipeline
        cat_pipe = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        # Combined preprocessor
        self.preprocessor = ColumnTransformer([
            ('num', num_pipe, self.num_cols),
            ('cat', cat_pipe, self.cat_cols)
        ], remainder='drop')
        
        logger.info("Preprocessing pipeline built successfully")
        
        return self.preprocessor
    
    def get_target_names(self) -> List[str]:
        """
        Get formatted target names for classification report
        
        Returns:
            List of formatted target names
        """
        if self.clases_reales is None:
            return []
        
        return [f"{i}-{name}" for i, name in enumerate(self.clases_reales)]
