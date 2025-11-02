"""
Unit tests for dataset comparison
Validates that the refactored code produces identical results to the original
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import (
    CLEAN_DATA_PATH,
    REFACTORED_CLEAN_DATA_PATH,
    ORIGINAL_DATA_PATH,
    MODIFIED_DATA_PATH
)


class TestDatasetComparison:
    """
    Test suite for comparing original and refactored datasets
    """
    
    @pytest.fixture
    def df_original_clean(self):
        """Load original cleaned dataset"""
        return pd.read_csv(CLEAN_DATA_PATH)
    
    @pytest.fixture
    def df_refactored_clean(self):
        """Load refactored cleaned dataset"""
        return pd.read_csv(REFACTORED_CLEAN_DATA_PATH)
    
    def test_files_exist(self):
        """Test that all required files exist"""
        assert ORIGINAL_DATA_PATH.exists(), f"Original data not found: {ORIGINAL_DATA_PATH}"
        assert MODIFIED_DATA_PATH.exists(), f"Modified data not found: {MODIFIED_DATA_PATH}"
        assert CLEAN_DATA_PATH.exists(), f"Clean data not found: {CLEAN_DATA_PATH}"
        assert REFACTORED_CLEAN_DATA_PATH.exists(), f"Refactored clean data not found: {REFACTORED_CLEAN_DATA_PATH}"
    
    def test_shape_match(self, df_original_clean, df_refactored_clean):
        """Test that shapes match"""
        assert df_original_clean.shape == df_refactored_clean.shape, \
            f"Shape mismatch: {df_original_clean.shape} vs {df_refactored_clean.shape}"
    
    def test_columns_match(self, df_original_clean, df_refactored_clean):
        """Test that columns match"""
        assert set(df_original_clean.columns) == set(df_refactored_clean.columns), \
            "Columns don't match"
        assert list(df_original_clean.columns) == list(df_refactored_clean.columns), \
            "Column order doesn't match"
    
    def test_dtypes_match(self, df_original_clean, df_refactored_clean):
        """Test that data types match"""
        for col in df_original_clean.columns:
            assert df_original_clean[col].dtype == df_refactored_clean[col].dtype, \
                f"Dtype mismatch in {col}: {df_original_clean[col].dtype} vs {df_refactored_clean[col].dtype}"
    
    def test_no_missing_values(self, df_original_clean, df_refactored_clean):
        """Test that both datasets have no missing values"""
        assert df_original_clean.isnull().sum().sum() == 0, \
            "Original clean dataset has missing values"
        assert df_refactored_clean.isnull().sum().sum() == 0, \
            "Refactored clean dataset has missing values"
    
    def test_numeric_values_match(self, df_original_clean, df_refactored_clean):
        """Test that numeric values match (with tolerance)"""
        numeric_cols = df_original_clean.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            assert np.allclose(
                df_original_clean[col],
                df_refactored_clean[col],
                rtol=1e-6,
                atol=1e-6,
                equal_nan=True
            ), f"Numeric values don't match in column: {col}"
    
    def test_categorical_values_match(self, df_original_clean, df_refactored_clean):
        """Test that categorical values match"""
        categorical_cols = df_original_clean.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            # Compare while handling NaN values
            mask = df_original_clean[col].notna() & df_refactored_clean[col].notna()
            assert (df_original_clean.loc[mask, col] == df_refactored_clean.loc[mask, col]).all(), \
                f"Categorical values don't match in column: {col}"
    
    def test_identical_datasets(self, df_original_clean, df_refactored_clean):
        """Test that datasets are completely identical"""
        # This is the master test
        pd.testing.assert_frame_equal(
            df_original_clean,
            df_refactored_clean,
            check_dtype=True,
            check_exact=False,
            rtol=1e-6,
            atol=1e-6
        )


class TestDataCleaning:
    """
    Test suite for data cleaning operations
    """
    
    @pytest.fixture
    def df_modified(self):
        """Load modified dataset"""
        return pd.read_csv(MODIFIED_DATA_PATH)
    
    @pytest.fixture
    def df_refactored_clean(self):
        """Load refactored cleaned dataset"""
        return pd.read_csv(REFACTORED_CLEAN_DATA_PATH)
    
    def test_mixed_type_col_removed(self, df_refactored_clean):
        """Test that mixed_type_col was removed"""
        assert 'mixed_type_col' not in df_refactored_clean.columns, \
            "mixed_type_col should be removed"
    
    def test_correct_columns_present(self, df_refactored_clean):
        """Test that all expected columns are present"""
        expected_cols = [
            'Gender', 'Age', 'Height', 'Weight', 'family_history_with_overweight',
            'FAVC', 'FCVC', 'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE',
            'CALC', 'MTRANS', 'NObeyesdad'
        ]
        
        assert set(df_refactored_clean.columns) == set(expected_cols), \
            "Column set doesn't match expected"
    
    def test_numeric_ranges(self, df_refactored_clean):
        """Test that numeric values are within realistic ranges"""
        assert df_refactored_clean['Age'].between(14, 100).all(), "Age out of range"
        assert df_refactored_clean['Height'].between(1.0, 2.5).all(), "Height out of range"
        assert df_refactored_clean['Weight'].between(20, 200).all(), "Weight out of range"
        assert df_refactored_clean['FCVC'].between(1, 3).all(), "FCVC out of range"
        assert df_refactored_clean['NCP'].between(1, 4).all(), "NCP out of range"
        assert df_refactored_clean['CH2O'].between(1, 3).all(), "CH2O out of range"
        assert df_refactored_clean['FAF'].between(0, 3).all(), "FAF out of range"
        assert df_refactored_clean['TUE'].between(0, 2).all(), "TUE out of range"
    
    def test_categorical_normalization(self, df_refactored_clean):
        """Test that categorical values are properly normalized"""
        # Gender should be Title Case
        assert df_refactored_clean['Gender'].isin(['Male', 'Female']).all(), \
            "Gender not properly normalized"
        
        # Binary columns should be lowercase
        binary_cols = ['family_history_with_overweight', 'FAVC', 'SMOKE', 'SCC']
        for col in binary_cols:
            assert df_refactored_clean[col].isin(['yes', 'no']).all(), \
                f"{col} not properly normalized to lowercase"
        
        # NObeyesdad should be lowercase with underscores
        expected_nobeyesdad = [
            'normal_weight', 'overweight_level_i', 'overweight_level_ii',
            'obesity_type_i', 'obesity_type_ii', 'obesity_type_iii',
            'insufficient_weight'
        ]
        assert df_refactored_clean['NObeyesdad'].isin(expected_nobeyesdad).all(), \
            "NObeyesdad not properly normalized"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
