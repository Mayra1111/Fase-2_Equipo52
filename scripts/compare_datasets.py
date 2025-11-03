"""
Script to compare the original cleaned dataset with the refactored one
This validates that the refactored code produces identical results
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import CLEAN_DATA_PATH, REFACTORED_CLEAN_DATA_PATH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def compare_datasets(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    name1: str = "Dataset 1",
    name2: str = "Dataset 2",
    tolerance: float = 1e-6
) -> dict:
    """
    Compare two datasets in detail
    
    Args:
        df1: First dataset
        df2: Second dataset
        name1: Name of first dataset
        name2: Name of second dataset
        tolerance: Numerical tolerance for comparisons
        
    Returns:
        Dictionary with comparison results
    """
    results = {
        "identical": False,
        "shape_match": False,
        "columns_match": False,
        "dtypes_match": False,
        "values_match": False,
        "differences": []
    }
    
    logger.info("="*70)
    logger.info(f"COMPARING: {name1} vs {name2}")
    logger.info("="*70)
    
    # 1. Compare shapes
    logger.info(f"\n1. Shape Comparison:")
    logger.info(f"   {name1}: {df1.shape}")
    logger.info(f"   {name2}: {df2.shape}")
    
    if df1.shape == df2.shape:
        results["shape_match"] = True
        logger.info("   ✓ Shapes match!")
    else:
        results["differences"].append(f"Shape mismatch: {df1.shape} vs {df2.shape}")
        logger.warning(f"   ✗ Shape mismatch!")
        return results
    
    # 2. Compare columns
    logger.info(f"\n2. Columns Comparison:")
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    if cols1 == cols2:
        results["columns_match"] = True
        logger.info(f"   ✓ Columns match! ({len(cols1)} columns)")
    else:
        results["differences"].append(f"Columns mismatch")
        logger.warning(f"   ✗ Columns don't match!")
        logger.warning(f"   Only in {name1}: {cols1 - cols2}")
        logger.warning(f"   Only in {name2}: {cols2 - cols1}")
        return results
    
    # 3. Compare dtypes
    logger.info(f"\n3. Data Types Comparison:")
    dtypes_match = True
    for col in df1.columns:
        if df1[col].dtype != df2[col].dtype:
            dtypes_match = False
            results["differences"].append(f"Dtype mismatch in {col}: {df1[col].dtype} vs {df2[col].dtype}")
            logger.warning(f"   ✗ {col}: {df1[col].dtype} vs {df2[col].dtype}")
    
    if dtypes_match:
        results["dtypes_match"] = True
        logger.info("   ✓ All data types match!")
    else:
        logger.warning("   ✗ Some data types don't match!")
    
    # 4. Compare values
    logger.info(f"\n4. Values Comparison:")
    values_match = True
    
    for col in df1.columns:
        # Handle numeric columns with tolerance
        if df1[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
            if not np.allclose(df1[col], df2[col], rtol=tolerance, atol=tolerance, equal_nan=True):
                values_match = False
                diff_mask = ~np.isclose(df1[col], df2[col], rtol=tolerance, atol=tolerance, equal_nan=True)
                diff_count = diff_mask.sum()
                results["differences"].append(f"Numeric differences in {col}: {diff_count} values")
                logger.warning(f"   ✗ {col}: {diff_count} different values")
                
                # Show sample of differences
                if diff_count > 0:
                    sample_idx = df1[diff_mask].index[:5]
                    logger.warning(f"      Sample differences:")
                    for idx in sample_idx:
                        logger.warning(f"        Row {idx}: {df1.loc[idx, col]} vs {df2.loc[idx, col]}")
        
        # Handle categorical columns
        else:
            if not df1[col].equals(df2[col]):
                values_match = False
                diff_mask = df1[col] != df2[col]
                
                # Handle NaN comparisons for categorical
                nan_mask1 = df1[col].isna()
                nan_mask2 = df2[col].isna()
                if not nan_mask1.equals(nan_mask2):
                    diff_count = (~(nan_mask1 == nan_mask2)).sum()
                else:
                    diff_count = diff_mask.sum()
                
                results["differences"].append(f"Categorical differences in {col}: {diff_count} values")
                logger.warning(f"   ✗ {col}: {diff_count} different values")
                
                # Show sample of differences
                if diff_count > 0 and diff_count < len(df1):
                    sample_idx = df1[diff_mask].index[:5] if diff_mask.sum() > 0 else []
                    if len(sample_idx) > 0:
                        logger.warning(f"      Sample differences:")
                        for idx in sample_idx:
                            logger.warning(f"        Row {idx}: '{df1.loc[idx, col]}' vs '{df2.loc[idx, col]}'")
    
    if values_match:
        results["values_match"] = True
        logger.info("   ✓ All values match!")
    else:
        logger.warning("   ✗ Some values don't match!")
    
    # 5. Summary
    logger.info(f"\n5. Summary:")
    logger.info(f"   Shape match: {'✓' if results['shape_match'] else '✗'}")
    logger.info(f"   Columns match: {'✓' if results['columns_match'] else '✗'}")
    logger.info(f"   Dtypes match: {'✓' if results['dtypes_match'] else '✗'}")
    logger.info(f"   Values match: {'✓' if results['values_match'] else '✗'}")
    
    results["identical"] = all([
        results["shape_match"],
        results["columns_match"],
        results["dtypes_match"],
        results["values_match"]
    ])
    
    if results["identical"]:
        logger.info("\n" + "="*10)
        logger.info("DATASETS ARE IDENTICAL!")
        logger.info("="*10)
    else:
        logger.warning("\n" + "="*10)
        logger.warning("DATASETS HAVE DIFFERENCES")
        logger.warning("="*10)
        logger.warning(f"Total differences found: {len(results['differences'])}")
    
    return results


def main():
    """
    Main function to compare datasets
    """
    try:
        logger.info("Loading datasets for comparison...")
        
        # Load original cleaned dataset
        logger.info(f"Loading original cleaned dataset: {CLEAN_DATA_PATH}")
        df_original = pd.read_csv(CLEAN_DATA_PATH)
        logger.info(f"✓ Original loaded: {df_original.shape}")
        
        # Load refactored cleaned dataset
        logger.info(f"Loading refactored cleaned dataset: {REFACTORED_CLEAN_DATA_PATH}")
        df_refactored = pd.read_csv(REFACTORED_CLEAN_DATA_PATH)
        logger.info(f"✓ Refactored loaded: {df_refactored.shape}")
        
        # Compare datasets
        results = compare_datasets(
            df_original,
            df_refactored,
            name1="Original Cleaned (Notebook)",
            name2="Refactored Cleaned (Pipeline)",
            tolerance=1e-6
        )
        
        # Return appropriate exit code
        return 0 if results["identical"] else 1
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        logger.error("Make sure both datasets exist:")
        logger.error(f"  1. {CLEAN_DATA_PATH}")
        logger.error(f"  2. {REFACTORED_CLEAN_DATA_PATH}")
        logger.error("\nRun the EDA pipeline first: python scripts/run_eda.py")
        return 1
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
