"""
Data loading module for the Obesity ML Project
Handles loading of datasets with proper error handling
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """
    Data loader class for handling dataset loading operations
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize DataLoader
        
        Args:
            data_path: Path to the data file
        """
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        
    def load_data(self, **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            **kwargs: Additional arguments to pass to pd.read_csv
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            pd.errors.EmptyDataError: If file is empty
        """
        logger.info(f"Loading data from: {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        try:
            self.df = pd.read_csv(self.data_path, **kwargs)
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            logger.info(f"Columns: {list(self.df.columns)}")
            return self.df
            
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty data file: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the loaded DataFrame
        
        Returns:
            DataFrame if loaded, None otherwise
        """
        if self.df is None:
            logger.warning("Data not loaded yet. Call load_data() first.")
        return self.df
    
    def get_info(self) -> dict:
        """
        Get basic information about the loaded data
        
        Returns:
            Dictionary with data information
        """
        if self.df is None:
            return {"error": "No data loaded"}
        
        return {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "total_missing": self.df.isnull().sum().sum()
        }
