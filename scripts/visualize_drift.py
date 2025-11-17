"""
Script to generate visualizations for data drift detection
Creates comparison plots for distributions and performance metrics
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    INTERIM_DATA_DIR,
    REPORTS_DIR,
    NUMERIC_COLUMNS,
    FIGURES_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def load_data_and_report():
    """
    Load baseline data, drifted data, and drift report

    Returns:
        Tuple of (df_baseline, df_drifted, report)
    """
    baseline_path = REFACTORED_CLEAN_DATA_PATH
    drifted_path = INTERIM_DATA_DIR / "dataset_with_drift.csv"
    report_path = REPORTS_DIR / "drift" / "drift_report.json"

    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline dataset not found: {baseline_path}")

    if not drifted_path.exists():
        raise FileNotFoundError(f"Drifted dataset not found: {drifted_path}")

    df_baseline = pd.read_csv(baseline_path)
    df_drifted = pd.read_csv(drifted_path)

    report = None
    if report_path.exists():
        with open(report_path, 'r') as f:
            report = json.load(f)

    return df_baseline, df_drifted, report


def plot_feature_distributions(
    df_baseline: pd.DataFrame,
    df_drifted: pd.DataFrame,
    features: list,
    output_dir: Path
):
    """
    Plot distribution comparisons for key features

    Args:
        df_baseline: Baseline dataset
        df_drifted: Drifted dataset
        features: List of feature names to plot
        output_dir: Output directory for figures
    """
    logger.info("Creating feature distribution plots...")

    n_features = len(features)
    n_cols = 3
    n_rows = (n_features + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    axes = axes.flatten() if n_features > 1 else [axes]

    for idx, feature in enumerate(features):
        if feature not in df_baseline.columns or feature not in df_drifted.columns:
            continue

        ax = axes[idx]

        # Plot distributions
        ax.hist(
            df_baseline[feature].dropna(),
            bins=30,
            alpha=0.6,
            label='Baseline',
            color='blue',
            density=True
        )
        ax.hist(
            df_drifted[feature].dropna(),
            bins=30,
            alpha=0.6,
            label='With Drift',
            color='red',
            density=True
        )

        # Add statistics
        baseline_mean = df_baseline[feature].mean()
        drifted_mean = df_drifted[feature].mean()
        shift_pct = ((drifted_mean - baseline_mean) / baseline_mean * 100) if baseline_mean != 0 else 0

        ax.axvline(baseline_mean, color='blue', linestyle='--', linewidth=2, label=f'Baseline Mean: {baseline_mean:.2f}')
        ax.axvline(drifted_mean, color='red', linestyle='--', linewidth=2, label=f'Drifted Mean: {drifted_mean:.2f}')

        ax.set_title(f'{feature}\n(Shift: {shift_pct:+.1f}%)', fontsize=12, fontweight='bold')
        ax.set_xlabel(feature)
        ax.set_ylabel('Density')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_features, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()

    output_path = output_dir / "10_drift_distributions.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Distribution plot saved to: {output_path}")
    plt.close()


def plot_performance_comparison(
    report: dict,
    output_dir: Path
):
    """
    Plot performance metrics comparison

    Args:
        report: Drift report dictionary
        output_dir: Output directory for figures
    """
    logger.info("Creating performance comparison plot...")

    if not report or 'baseline_metrics' not in report:
        logger.warning("No report available for performance comparison")
        return

    baseline_metrics = report['baseline_metrics']
    current_metrics = report['current_metrics']

    metrics = ['accuracy', 'precision', 'recall', 'f1']
    baseline_values = [baseline_metrics.get(m, 0) for m in metrics]
    current_values = [current_metrics.get(m, 0) for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline', color='blue', alpha=0.7)
    bars2 = ax.bar(x + width/2, current_values, width, label='With Drift', color='red', alpha=0.7)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)

    # Calculate and show degradation
    degradations = []
    for m in metrics:
        baseline = baseline_metrics.get(m, 0)
        current = current_metrics.get(m, 0)
        degradation = ((baseline - current) / baseline * 100) if baseline > 0 else 0
        degradations.append(degradation)

    ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance: Baseline vs Drifted Data', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.capitalize() for m in metrics])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1.1])

    # Add degradation annotations
    for i, (m, deg) in enumerate(zip(metrics, degradations)):
        if deg > 0:
            color = 'red' if deg > 5 else 'orange'
            ax.text(i, max(baseline_values[i], current_values[i]) + 0.05,
                   f'{deg:.1f}%↓',
                   ha='center', va='bottom', fontsize=10, color=color, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / "11_drift_performance_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Performance comparison plot saved to: {output_path}")
    plt.close()


def plot_psi_heatmap(
    report: dict,
    output_dir: Path
):
    """
    Plot PSI values as heatmap

    Args:
        report: Drift report dictionary
        output_dir: Output directory for figures
    """
    logger.info("Creating PSI heatmap...")

    if not report or 'feature_drift' not in report:
        logger.warning("No feature drift data available")
        return

    feature_drift = report['feature_drift']

    # Extract PSI values
    features = []
    psi_values = []
    alert_status = []

    for feature, metrics in feature_drift.items():
        features.append(feature)
        psi_values.append(metrics.get('psi', 0))
        alert_status.append('High' if metrics.get('psi_alert', False) else 'Low')

    # Create DataFrame for heatmap
    psi_df = pd.DataFrame({
        'Feature': features,
        'PSI': psi_values,
        'Alert': alert_status
    }).sort_values('PSI', ascending=False)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, max(6, len(features) * 0.5)))

    # Create color map based on PSI values
    colors = []
    for psi in psi_df['PSI']:
        if psi > 0.2:
            colors.append('red')
        elif psi > 0.1:
            colors.append('orange')
        else:
            colors.append('green')

    bars = ax.barh(psi_df['Feature'], psi_df['PSI'], color=colors, alpha=0.7)

    # Add threshold line
    ax.axvline(0.2, color='red', linestyle='--', linewidth=2, label='Alert Threshold (0.2)')
    ax.axvline(0.1, color='orange', linestyle='--', linewidth=1, label='Warning Threshold (0.1)')

    # Add value labels
    for i, (bar, psi) in enumerate(zip(bars, psi_df['PSI'])):
        ax.text(psi + 0.01, bar.get_y() + bar.get_height()/2,
               f'{psi:.3f}',
               va='center', fontsize=9)

    ax.set_xlabel('PSI (Population Stability Index)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Feature', fontsize=12, fontweight='bold')
    ax.set_title('Data Drift Detection: PSI by Feature', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    output_path = output_dir / "12_drift_psi_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"PSI heatmap saved to: {output_path}")
    plt.close()


def main():
    """
    Main function to generate all drift visualizations
    """
    logger.info("="*70)
    logger.info("GENERATING DRIFT VISUALIZATIONS")
    logger.info("="*70)

    output_dir = FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load data and report
        logger.info("\nLoading data and drift report...")
        df_baseline, df_drifted, report = load_data_and_report()

        logger.info(f"Baseline dataset: {df_baseline.shape}")
        logger.info(f"Drifted dataset: {df_drifted.shape}")

        # Key features to visualize
        key_features = ['Age', 'Weight', 'Height', 'FCVC', 'NCP', 'CH2O']
        key_features = [f for f in key_features if f in df_baseline.columns]

        # 1. Feature distributions
        logger.info("\n1. Creating feature distribution plots...")
        plot_feature_distributions(df_baseline, df_drifted, key_features, output_dir)

        # 2. Performance comparison
        if report:
            logger.info("\n2. Creating performance comparison plot...")
            plot_performance_comparison(report, output_dir)

            # 3. PSI heatmap
            logger.info("\n3. Creating PSI heatmap...")
            plot_psi_heatmap(report, output_dir)
        else:
            logger.warning("No drift report found. Run detect_drift.py first.")

        logger.info("\n" + "="*70)
        logger.info("✓ All visualizations generated successfully!")
        logger.info(f"✓ Figures saved to: {output_dir}")
        logger.info("="*70)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        logger.error("Please run simulate_drift.py and detect_drift.py first")
        return 1
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
