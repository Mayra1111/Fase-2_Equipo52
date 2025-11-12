"""
Data cleaning module for the Obesity ML Project
Implements the complete data cleaning pipeline using OOP and Scikit-Learn transformers
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from ..utils.config import (
    NUMERIC_COLUMNS, CATEGORICAL_COLUMNS, COLUMNS_TO_DROP,
    VALUE_RANGES, NA_VALUES, NOBEYESDAD_MAPPING, LOWERCASE_BINARY_COLS
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ColumnDropper(BaseEstimator, TransformerMixin):
    """
    Transformer to drop specified columns
    """
    
    def __init__(self, columns_to_drop: List[str]):
        self.columns_to_drop = columns_to_drop
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        existing_cols = [col for col in self.columns_to_drop if col in X_copy.columns]
        if existing_cols:
            X_copy = X_copy.drop(existing_cols, axis=1)
            logger.info(f"✓ Dropped columns: {existing_cols}")
        return X_copy


class TextCleaner(BaseEstimator, TransformerMixin):
    """
    Transformer to clean text in object columns
    """
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Cleaning text data...")
        
        for col in X_copy.columns:
            if X_copy[col].dtype == 'object':
                # Convert to string and strip whitespace
                X_copy[col] = X_copy[col].astype(str).str.strip()
                
                # Clean internal multiple spaces
                X_copy[col] = X_copy[col].str.replace(r'\s+', ' ', regex=True)
                
                # Clean special characters
                X_copy[col] = X_copy[col].str.replace(r'[^\w\s\-_\.]', '', regex=True)
        
        logger.info("✓ Text cleaned")
        return X_copy


class NAHandler(BaseEstimator, TransformerMixin):
    """
    Transformer to handle N/A values and variations
    """
    
    def __init__(self, na_values: List[str]):
        self.na_values = na_values
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Handling N/A values and variations...")
        
        for col in X_copy.columns:
            if X_copy[col].dtype == 'object':
                # Replace all N/A variations with NaN
                X_copy[col] = X_copy[col].replace(self.na_values, np.nan)
        
        logger.info("✓ N/A values converted to NaN")
        return X_copy


class NumericConverter(BaseEstimator, TransformerMixin):
    """
    Transformer to convert specified columns to numeric
    """
    
    def __init__(self, numeric_columns: List[str]):
        self.numeric_columns = numeric_columns
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Converting numeric columns...")
        
        for col in self.numeric_columns:
            if col in X_copy.columns:
                # Clean numeric values before converting
                X_copy[col] = X_copy[col].astype(str).str.replace(r'[^\d\.\-]', '', regex=True)
                X_copy[col] = pd.to_numeric(X_copy[col], errors='coerce')
        
        logger.info("✓ Numeric columns converted")
        return X_copy


class OutlierHandler(BaseEstimator, TransformerMixin):
    """
    Transformer to detect and correct outliers based on realistic value ranges
    """
    
    def __init__(self, value_ranges: Dict[str, Tuple[float, float]]):
        self.value_ranges = value_ranges
        self.outliers_corrected = 0
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Validating realistic ranges and correcting outliers...")
        self.outliers_corrected = 0
        
        for col, (min_val, max_val) in self.value_ranges.items():
            if col in X_copy.columns:
                # Identify outliers
                outliers_mask = (X_copy[col] < min_val) | (X_copy[col] > max_val)
                outlier_count = outliers_mask.sum()
                
                if outlier_count > 0:
                    logger.info(f"  {col}: {outlier_count} values outside range [{min_val}, {max_val}]")
                    
                    # Replace outliers with median (robust to outliers)
                    median_val = X_copy[col].median()
                    X_copy.loc[outliers_mask, col] = median_val
                    self.outliers_corrected += outlier_count
                    logger.info(f"    ✓ Replaced with median: {median_val:.2f}")
        
        logger.info(f"✓ Total outliers corrected: {self.outliers_corrected}")
        return X_copy


class CategoricalNormalizer(BaseEstimator, TransformerMixin):
    """
    Transformer to normalize categorical values
    """
    
    def __init__(
        self,
        lowercase_cols: List[str],
        nobeyesdad_mapping: Dict[str, str]
    ):
        self.lowercase_cols = lowercase_cols
        self.nobeyesdad_mapping = nobeyesdad_mapping
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Normalizing categorical values...")
        
        # 1. Normalize Gender (Title Case)
        if 'Gender' in X_copy.columns:
            X_copy['Gender'] = X_copy['Gender'].str.title()
        
        # 2. Normalize binary variables (lowercase)
        for col in self.lowercase_cols:
            if col in X_copy.columns:
                X_copy[col] = X_copy[col].str.lower()
        
        # 3. Normalize CAEC (Title Case, but 'no' in lowercase)
        if 'CAEC' in X_copy.columns:
            X_copy['CAEC'] = X_copy['CAEC'].str.title()
            X_copy.loc[X_copy['CAEC'] == 'No', 'CAEC'] = 'no'
        
        # 4. Normalize MTRANS (Title Case)
        if 'MTRANS' in X_copy.columns:
            X_copy['MTRANS'] = X_copy['MTRANS'].str.title()
        
        # 5. Normalize CALC (Title Case, but 'no' in lowercase)
        if 'CALC' in X_copy.columns:
            X_copy['CALC'] = X_copy['CALC'].str.title()
            X_copy.loc[X_copy['CALC'] == 'No', 'CALC'] = 'no'
        
        # 6. Normalize NObeyesdad (target variable - very important)
        if 'NObeyesdad' in X_copy.columns:
            logger.info("Normalizing target variable NObeyesdad...")
            for old_val, new_val in self.nobeyesdad_mapping.items():
                X_copy['NObeyesdad'] = X_copy['NObeyesdad'].replace(old_val, new_val)
            logger.info("✓ Target variable NObeyesdad normalized")
        
        logger.info("✓ Categorical values normalized")
        return X_copy


class MissingValueImputer(BaseEstimator, TransformerMixin):
    """
    Transformer to impute missing values
    - Numeric columns: median
    - Categorical columns: mode
    """
    
    def __init__(self, numeric_columns: List[str]):
        self.numeric_columns = numeric_columns
        self.numeric_imputer = None
        self.categorical_imputers = {}
        
    def fit(self, X, y=None):
        # Fit numeric imputer
        numeric_cols_present = [col for col in self.numeric_columns if col in X.columns]
        if numeric_cols_present:
            self.numeric_imputer = SimpleImputer(strategy='median')
            self.numeric_imputer.fit(X[numeric_cols_present])
        
        # Fit categorical imputers (one per column for mode)
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if X[col].isnull().any():
                mode_val = X[col].mode()[0] if not X[col].mode().empty else 'Unknown'
                self.categorical_imputers[col] = mode_val
        
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        logger.info("Imputing missing values...")
        
        # Impute numeric columns
        numeric_cols_present = [col for col in self.numeric_columns if col in X_copy.columns]
        if numeric_cols_present and self.numeric_imputer is not None:
            for col in numeric_cols_present:
                if X_copy[col].isnull().any():
                    missing_count = X_copy[col].isnull().sum()
                    median_val = X_copy[col].median()
                    X_copy[col] = X_copy[col].fillna(median_val)
                    logger.info(f"  {col}: {missing_count} missing values replaced with median ({median_val:.2f})")
        
        # Impute categorical columns
        for col, mode_val in self.categorical_imputers.items():
            if col in X_copy.columns and X_copy[col].isnull().any():
                missing_count = X_copy[col].isnull().sum()
                X_copy[col] = X_copy[col].fillna(mode_val)
                logger.info(f"  {col}: {missing_count} missing values replaced with mode ({mode_val})")
        
        logger.info("✓ Missing values imputed")
        return X_copy


class DataCleaner:
    """
    Main data cleaning class that orchestrates the entire cleaning pipeline
    This class replicates exactly the cleaning process from the original notebook
    """
    
    def __init__(self):
        """
        Initialize DataCleaner with configuration from config.py
        """
        self.pipeline = None
        self.original_shape = None
        self.cleaned_shape = None
        self.outliers_corrected = 0
        self._build_pipeline()
        logger.info("DataCleaner initialized")
    
    def _build_pipeline(self):
        """
        Build the complete cleaning pipeline using Scikit-Learn Pipeline
        """
        self.pipeline = Pipeline([
            ('drop_columns', ColumnDropper(COLUMNS_TO_DROP)),
            ('text_cleaner', TextCleaner()),
            ('na_handler', NAHandler(NA_VALUES)),
            ('numeric_converter', NumericConverter(NUMERIC_COLUMNS)),
            ('outlier_handler', OutlierHandler(VALUE_RANGES)),
            ('categorical_normalizer', CategoricalNormalizer(LOWERCASE_BINARY_COLS, NOBEYESDAD_MAPPING)),
            ('missing_imputer', MissingValueImputer(NUMERIC_COLUMNS))
        ])
        logger.info("Cleaning pipeline built successfully")
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform the data through the cleaning pipeline
        
        Args:
            df: Input DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("="*50)
        logger.info("STARTING DATA CLEANING PROCESS")
        logger.info("="*50)
        
        self.original_shape = df.shape
        logger.info(f"Original dataset shape: {self.original_shape}")
        logger.info(f"Original missing values: {df.isnull().sum().sum()}")
        
        # Apply the pipeline
        df_cleaned = self.pipeline.fit_transform(df)
        
        self.cleaned_shape = df_cleaned.shape
        logger.info("="*50)
        logger.info("DATA CLEANING COMPLETED")
        logger.info("="*50)
        logger.info(f"Cleaned dataset shape: {self.cleaned_shape}")
        logger.info(f"Remaining missing values: {df_cleaned.isnull().sum().sum()}")
        logger.info(f"Rows preserved: {self.cleaned_shape[0]} / {self.original_shape[0]}")
        
        return df_cleaned
    
    def get_cleaning_report(self) -> Dict:
        """
        Get a report of the cleaning process
        
        Returns:
            Dictionary with cleaning statistics
        """
        return {
            "original_shape": self.original_shape,
            "cleaned_shape": self.cleaned_shape,
            "rows_preserved": self.cleaned_shape[0] if self.cleaned_shape else 0,
            "columns_final": self.cleaned_shape[1] if self.cleaned_shape else 0
        }
