"""
Script to simulate data drift by modifying the baseline dataset
Creates a new dataset with shifted distributions to test drift detection
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import REFACTORED_CLEAN_DATA_PATH, INTERIM_DATA_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


def simulate_drift(
    input_path: Path,
    output_path: Path,
    age_shift_pct: float = 0.10,      # 10% increase in age
    weight_shift_pct: float = 0.15,   # 15% increase in weight
    height_shift_pct: float = 0.05,    # 5% increase in height
    add_noise: bool = True,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Simulate data drift by modifying numeric distributions

    This function creates a dataset with shifted distributions to simulate
    real-world scenarios where data changes over time (e.g., population aging,
    lifestyle changes affecting weight/height distributions).

    Args:
        input_path: Path to baseline dataset
        output_path: Path to save drifted dataset
        age_shift_pct: Percentage shift in age distribution (default: 10%)
        weight_shift_pct: Percentage shift in weight distribution (default: 15%)
        height_shift_pct: Percentage shift in height distribution (default: 5%)
        add_noise: Whether to add random noise to other numeric features
        random_state: Random seed for reproducibility

    Returns:
        DataFrame with simulated drift
    """
    logger.info("="*70)
    logger.info("SIMULATING DATA DRIFT")
    logger.info("="*70)

    # Load baseline data
    logger.info(f"Loading baseline data from: {input_path}")
    df_baseline = pd.read_csv(input_path)
    logger.info(f"Baseline dataset shape: {df_baseline.shape}")

    # Create copy for modification
    df_drifted = df_baseline.copy()

    np.random.seed(random_state)

    # 1. Shift Age distribution (increase mean age by 10%)
    if 'Age' in df_drifted.columns:
        baseline_age_mean = df_drifted['Age'].mean()
        age_shift = baseline_age_mean * age_shift_pct

        logger.info(f"Shifting Age distribution:")
        logger.info(f"  Baseline mean: {baseline_age_mean:.2f}")
        logger.info(f"  Shift amount: {age_shift:.2f} ({age_shift_pct*100:.1f}%)")

        # Apply shift with some randomness
        df_drifted['Age'] = df_drifted['Age'] + age_shift + np.random.normal(0, age_shift * 0.1, len(df_drifted))
        df_drifted['Age'] = df_drifted['Age'].clip(lower=14, upper=100)  # Keep realistic range

        logger.info(f"  New mean: {df_drifted['Age'].mean():.2f}")

    # 2. Shift Weight distribution (increase mean weight by 15%)
    if 'Weight' in df_drifted.columns:
        baseline_weight_mean = df_drifted['Weight'].mean()
        weight_shift = baseline_weight_mean * weight_shift_pct

        logger.info(f"Shifting Weight distribution:")
        logger.info(f"  Baseline mean: {baseline_weight_mean:.2f}")
        logger.info(f"  Shift amount: {weight_shift:.2f} ({weight_shift_pct*100:.1f}%)")

        # Apply shift with some randomness
        df_drifted['Weight'] = df_drifted['Weight'] + weight_shift + np.random.normal(0, weight_shift * 0.1, len(df_drifted))
        df_drifted['Weight'] = df_drifted['Weight'].clip(lower=20, upper=200)  # Keep realistic range

        logger.info(f"  New mean: {df_drifted['Weight'].mean():.2f}")

    # 3. Shift Height distribution (increase mean height by 5%)
    if 'Height' in df_drifted.columns:
        baseline_height_mean = df_drifted['Height'].mean()
        height_shift = baseline_height_mean * height_shift_pct

        logger.info(f"Shifting Height distribution:")
        logger.info(f"  Baseline mean: {baseline_height_mean:.2f}")
        logger.info(f"  Shift amount: {height_shift:.4f} ({height_shift_pct*100:.1f}%)")

        # Apply shift with some randomness
        df_drifted['Height'] = df_drifted['Height'] + height_shift + np.random.normal(0, height_shift * 0.1, len(df_drifted))
        df_drifted['Height'] = df_drifted['Height'].clip(lower=1.0, upper=2.5)  # Keep realistic range

        logger.info(f"  New mean: {df_drifted['Height'].mean():.4f}")

    # 4. Add noise to other numeric features (simulate measurement errors or changes)
    if add_noise:
        numeric_cols = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
        for col in numeric_cols:
            if col in df_drifted.columns:
                # Add small random noise (2-5% of standard deviation)
                std = df_drifted[col].std()
                noise = np.random.normal(0, std * 0.03, len(df_drifted))
                df_drifted[col] = df_drifted[col] + noise

                # Clip to valid ranges
                if col == 'FCVC':
                    df_drifted[col] = df_drifted[col].clip(lower=1, upper=3)
                elif col == 'NCP':
                    df_drifted[col] = df_drifted[col].clip(lower=1, upper=4)
                elif col == 'CH2O':
                    df_drifted[col] = df_drifted[col].clip(lower=1, upper=3)
                elif col == 'FAF':
                    df_drifted[col] = df_drifted[col].clip(lower=0, upper=3)
                elif col == 'TUE':
                    df_drifted[col] = df_drifted[col].clip(lower=0, upper=2)

    # 5. Recalculate BMI if it exists (since Weight and Height changed)
    if 'BMI' in df_drifted.columns and 'Weight' in df_drifted.columns and 'Height' in df_drifted.columns:
        df_drifted['BMI'] = df_drifted['Weight'] / (df_drifted['Height'] ** 2)
        logger.info("Recalculated BMI based on new Weight and Height values")

    # Save drifted dataset
    logger.info(f"\nSaving drifted dataset to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_drifted.to_csv(output_path, index=False)
    logger.info(f"Drifted dataset saved. Shape: {df_drifted.shape}")

    # Summary statistics
    logger.info("\n" + "="*70)
    logger.info("DRIFT SIMULATION SUMMARY")
    logger.info("="*70)
    logger.info(f"Baseline dataset: {input_path.name}")
    logger.info(f"Drifted dataset: {output_path.name}")
    logger.info(f"\nFeature shifts applied:")
    logger.info(f"  Age: +{age_shift_pct*100:.1f}% (mean shift: {age_shift:.2f})")
    logger.info(f"  Weight: +{weight_shift_pct*100:.1f}% (mean shift: {weight_shift:.2f})")
    logger.info(f"  Height: +{height_shift_pct*100:.1f}% (mean shift: {height_shift:.4f})")
    logger.info(f"  Other numeric features: Added 3% noise")
    logger.info("="*70)

    return df_drifted


def main():
    """
    Main function to simulate data drift
    """
    # Define paths
    baseline_path = REFACTORED_CLEAN_DATA_PATH
    output_path = INTERIM_DATA_DIR / "dataset_with_drift.csv"

    # Check if baseline exists
    if not baseline_path.exists():
        logger.error(f"Baseline dataset not found: {baseline_path}")
        logger.error("Please run the EDA pipeline first: python scripts/run_eda.py")
        return 1

    try:
        # Simulate drift
        df_drifted = simulate_drift(
            input_path=baseline_path,
            output_path=output_path,
            age_shift_pct=0.10,      # 10% increase
            weight_shift_pct=0.15,    # 15% increase
            height_shift_pct=0.05,    # 5% increase
            add_noise=True,
            random_state=42
        )

        logger.info("\n✓ Drift simulation completed successfully!")
        logger.info(f"✓ Drifted dataset saved to: {output_path}")

        return 0

    except Exception as e:
        logger.error(f"Error simulating drift: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
