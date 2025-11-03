"""
Configuration file for the Obesity ML Project
Centralizes all project configurations and parameters
"""

from pathlib import Path
from typing import Dict, List, Tuple

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model directories
MODELS_DIR = PROJECT_ROOT / "models"

# Reports directories
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
METRICS_DIR = REPORTS_DIR / "metrics"

# MLflow tracking
MLFLOW_TRACKING_URI = "file:" + str(PROJECT_ROOT / "mlruns")
MLFLOW_EXPERIMENT_NAME = "obesity-eda-refactored"
MLFLOW_ML_EXPERIMENT_NAME = "Clasificacion_Niveles_Obesidad"

# Data file paths
ORIGINAL_DATA_PATH = INTERIM_DATA_DIR / "obesity_estimation_original.csv"
MODIFIED_DATA_PATH = RAW_DATA_DIR / "obesity_estimation_modified.csv"
CLEAN_DATA_PATH = INTERIM_DATA_DIR / "dataset_limpio.csv"
REFACTORED_CLEAN_DATA_PATH = INTERIM_DATA_DIR / "dataset_limpio_refactored.csv"

# Numeric columns definition
NUMERIC_COLUMNS: List[str] = [
    'Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE'
]

# Categorical columns definition
CATEGORICAL_COLUMNS: List[str] = [
    'Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 
    'SMOKE', 'SCC', 'CALC', 'MTRANS', 'NObeyesdad'
]

# Columns to drop
COLUMNS_TO_DROP: List[str] = ['mixed_type_col']

# Realistic value ranges for validation
VALUE_RANGES: Dict[str, Tuple[float, float]] = {
    'Age': (14, 100),      # Age in years
    'Height': (1.0, 2.5),  # Height in meters
    'Weight': (20, 200),   # Weight in kg
    'FCVC': (1, 3),        # Frequency of vegetable consumption
    'NCP': (1, 4),         # Number of main meals
    'CH2O': (1, 3),        # Water consumption
    'FAF': (0, 3),         # Physical activity frequency
    'TUE': (0, 2)          # Time using technology devices
}

# Values to replace with NaN
NA_VALUES: List[str] = [
    'N/A', 'n/a', 'NA', 'na', 'nan', 'NaN', 'NAN',
    'null', 'NULL', 'None', 'NONE',
    '?', 'unknown', 'bad', 'missing', 'MISSING',
    '', ' ', '  '
]

# NObeyesdad normalization mapping
NOBEYESDAD_MAPPING: Dict[str, str] = {
    # Already correct format
    'Normal_Weight': 'normal_weight',
    'Overweight_Level_I': 'overweight_level_i',
    'Overweight_Level_II': 'overweight_level_ii',
    'Obesity_Type_I': 'obesity_type_i',
    'Obesity_Type_II': 'obesity_type_ii',
    'Obesity_Type_III': 'obesity_type_iii',
    'Insufficient_Weight': 'insufficient_weight',
    # Problematic values from modified dataset
    'NORMAL_WEIGHT': 'normal_weight',
    'OVERWEIGHT_LEVEL_I': 'overweight_level_i',
    'OVERWEIGHT_LEVEL_II': 'overweight_level_ii',
    'OBESITY_TYPE_I': 'obesity_type_i',
    'OBESITY_TYPE_II': 'obesity_type_ii',
    'OBESITY_TYPE_III': 'obesity_type_iii',
    'INSUFFICIENT_WEIGHT': 'insufficient_weight',
    # Mixed case variations
    'nORMAL_wEIGHT': 'normal_weight',
    'oVERWEIGHT_lEVEL_i': 'overweight_level_i',
    'oVERWEIGHT_lEVEL_ii': 'overweight_level_ii',
    'oBESITY_tYPE_i': 'obesity_type_i',
    'oBESITY_tYPE_ii': 'obesity_type_ii',
    'oBESITY_tYPE_iii': 'obesity_type_iii',
    'iNSUFFICIENT_wEIGHT': 'insufficient_weight'
}

# Binary columns that should use lowercase
LOWERCASE_BINARY_COLS: List[str] = [
    'family_history_with_overweight', 'FAVC', 'SMOKE', 'SCC'
]

# Random seed for reproducibility
RANDOM_STATE = 42

# ML Hyperparameters
ML_TEST_SIZE = 0.2
ML_CV_SPLITS = 5
ML_RANDOM_SEARCH_ITER = 20

# RandomForest parameters
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = 10

# XGBoost parameters
XGB_N_ESTIMATORS = 200
XGB_MAX_DEPTH = 5
XGB_LEARNING_RATE = 0.1

# KNN parameters
KNN_N_NEIGHBORS = 5

# SVM parameters
SVM_KERNEL = 'linear'
SVM_C = 1.0

# XGBoost hyperparameter search space
XGB_PARAM_DIST = {
    'clf__n_estimators': [100, 200, 400],
    'clf__max_depth': [3, 5, 7],
    'clf__learning_rate': [0.01, 0.05, 0.1],
    'clf__subsample': [0.6, 0.8, 1.0],
    'clf__colsample_bytree': [0.6, 0.8, 1.0],
    'smote__k_neighbors': [1]
}
