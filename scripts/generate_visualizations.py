"""
Script to generate EDA visualizations from the cleaned dataset
This script generates all visualizations and saves them as PNG files
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.data.data_loader import DataLoader
from src.visualization.eda_visualizer import generate_eda_visualizations
from src.utils.config import REFACTORED_CLEAN_DATA_PATH, FIGURES_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main function to generate EDA visualizations
    """
    parser = argparse.ArgumentParser(description='Generate EDA visualizations')
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input CSV file (default: data/interim/dataset_limpio_refactored.csv)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Directory to save figures (default: reports/figures/)'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine input path
        input_path = Path(args.input) if args.input else REFACTORED_CLEAN_DATA_PATH
        output_dir = Path(args.output_dir) if args.output_dir else FIGURES_DIR
        
        logger.info("="*70)
        logger.info("STARTING EDA VISUALIZATION GENERATION")
        logger.info("="*70)
        logger.info(f"Input: {input_path}")
        logger.info(f"Output directory: {output_dir}")
        
        # Load data
        logger.info("\nLoading cleaned dataset...")
        data_loader = DataLoader(input_path)
        df = data_loader.load_data()
        logger.info(f"✓ Data loaded: {df.shape}")
        
        # Generate visualizations
        logger.info("\nGenerating visualizations...")
        visualizer = generate_eda_visualizations(df, output_dir=output_dir)
        
        logger.info("\n" + "="*70)
        logger.info("✓ VISUALIZATION GENERATION COMPLETED!")
        logger.info("="*70)
        logger.info(f"All visualizations saved to: {output_dir}")
        logger.info("\nGenerated files:")
        logger.info("  1. 01_dataset_overview.png")
        logger.info("  2. 02_numeric_distributions.png")
        logger.info("  3. 03_numeric_boxplots.png")
        logger.info("  4. 04_categorical_distributions.png")
        logger.info("  5. 05_target_distribution.png")
        logger.info("  6. 06_correlation_matrix.png")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        logger.error(f"Make sure the cleaned dataset exists at: {input_path}")
        logger.error("\nRun the EDA pipeline first: python scripts/run_eda.py")
        return 1
    except Exception as e:
        logger.error(f"Visualization generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
