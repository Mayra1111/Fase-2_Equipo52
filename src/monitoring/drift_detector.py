"""
Data Drift Detection Module
Implements statistical methods to detect data drift in production ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

from ..utils.logger import get_logger

logger = get_logger(__name__)


def calculate_psi(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    """
    Calculate Population Stability Index (PSI) between two distributions

    PSI measures how much a distribution has shifted over time.
    - PSI < 0.1: No significant change
    - PSI 0.1-0.2: Minor change (monitor)
    - PSI > 0.2: Significant change (alert)

    Args:
        expected: Baseline/reference distribution
        actual: Current/new distribution
        bins: Number of bins for discretization

    Returns:
        PSI value (float)
    """
    try:
        # Remove NaN values
        expected_clean = expected.dropna()
        actual_clean = actual.dropna()

        if len(expected_clean) == 0 or len(actual_clean) == 0:
            logger.warning("Empty series provided for PSI calculation")
            return np.nan

        # Create bins based on expected distribution
        min_val = min(expected_clean.min(), actual_clean.min())
        max_val = max(expected_clean.max(), actual_clean.max())

        # Handle edge case where min == max
        if min_val == max_val:
            return 0.0

        bin_edges = np.linspace(min_val, max_val, bins + 1)

        # Calculate expected and actual distributions
        expected_counts, _ = np.histogram(expected_clean, bins=bin_edges)
        actual_counts, _ = np.histogram(actual_clean, bins=bin_edges)

        # Normalize to probabilities
        expected_probs = expected_counts / len(expected_clean)
        actual_probs = actual_counts / len(actual_clean)

        # Avoid division by zero and log(0)
        epsilon = 1e-6
        expected_probs = np.where(expected_probs == 0, epsilon, expected_probs)
        actual_probs = np.where(actual_probs == 0, epsilon, actual_probs)

        # Calculate PSI
        psi = np.sum((actual_probs - expected_probs) * np.log(actual_probs / expected_probs))

        return float(psi)

    except Exception as e:
        logger.error(f"Error calculating PSI: {str(e)}")
        return np.nan


def compare_distributions(
    baseline: pd.Series,
    current: pd.Series,
    test_type: str = 'ks'
) -> Dict[str, float]:
    """
    Compare two distributions using statistical tests

    Args:
        baseline: Baseline distribution
        current: Current distribution to compare
        test_type: Type of test ('ks' for Kolmogorov-Smirnov, 'mannwhitney' for Mann-Whitney U)

    Returns:
        Dictionary with test statistics and p-value
    """
    try:
        baseline_clean = baseline.dropna()
        current_clean = current.dropna()

        if len(baseline_clean) == 0 or len(current_clean) == 0:
            return {
                'statistic': np.nan,
                'p_value': np.nan,
                'significant': False
            }

        # Validate test type before running test
        if test_type not in ['ks', 'mannwhitney']:
            raise ValueError(f"Unknown test type: {test_type}")

        if test_type == 'ks':
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(baseline_clean, current_clean)
        elif test_type == 'mannwhitney':
            # Mann-Whitney U test (non-parametric)
            statistic, p_value = stats.mannwhitneyu(baseline_clean, current_clean, alternative='two-sided')

        # Significance at 0.05 level
        significant = p_value < 0.05

        return {
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': significant
        }

    except ValueError:
        # Re-raise ValueError (invalid test type)
        raise
    except Exception as e:
        logger.error(f"Error comparing distributions: {str(e)}")
        return {
            'statistic': np.nan,
            'p_value': np.nan,
            'significant': False
        }


class DriftDetector:
    """
    Main class for detecting data drift in ML models
    """

    def __init__(
        self,
        psi_threshold: float = 0.2,
        accuracy_degradation_threshold: float = 0.05,
        accuracy_critical_threshold: float = 0.10
    ):
        """
        Initialize DriftDetector

        Args:
            psi_threshold: PSI threshold for drift alert (default: 0.2)
            accuracy_degradation_threshold: Accuracy degradation threshold for warning (default: 0.05 = 5%)
            accuracy_critical_threshold: Accuracy degradation threshold for critical alert (default: 0.10 = 10%)
        """
        self.psi_threshold = psi_threshold
        self.accuracy_degradation_threshold = accuracy_degradation_threshold
        self.accuracy_critical_threshold = accuracy_critical_threshold

        logger.info(f"DriftDetector initialized with PSI threshold: {psi_threshold}")

    def calculate_feature_drift(
        self,
        baseline_data: pd.DataFrame,
        current_data: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Calculate drift metrics for each numeric feature

        Args:
            baseline_data: Baseline dataset
            current_data: Current dataset to compare
            numeric_columns: List of numeric columns to analyze (if None, auto-detect)

        Returns:
            Dictionary with drift metrics per feature
        """
        if numeric_columns is None:
            numeric_columns = baseline_data.select_dtypes(include=[np.number]).columns.tolist()

        drift_results = {}

        for col in numeric_columns:
            if col not in baseline_data.columns or col not in current_data.columns:
                logger.warning(f"Column {col} not found in one of the datasets")
                continue

            baseline_series = baseline_data[col]
            current_series = current_data[col]

            # Calculate PSI
            psi = calculate_psi(baseline_series, current_series)

            # Compare distributions
            ks_test = compare_distributions(baseline_series, current_series, test_type='ks')

            # Calculate basic statistics
            baseline_mean = baseline_series.mean()
            current_mean = current_series.mean()
            mean_shift = current_mean - baseline_mean
            mean_shift_pct = (mean_shift / baseline_mean * 100) if baseline_mean != 0 else 0

            baseline_std = baseline_series.std()
            current_std = current_series.std()
            std_shift = current_std - baseline_std
            std_shift_pct = (std_shift / baseline_std * 100) if baseline_std != 0 else 0

            # Determine drift status
            has_drift = psi > self.psi_threshold or ks_test['significant']
            drift_severity = 'none'
            if psi > self.psi_threshold:
                drift_severity = 'high' if psi > 0.5 else 'medium'
            elif ks_test['significant']:
                drift_severity = 'low'

            drift_results[col] = {
                'psi': psi,
                'psi_alert': psi > self.psi_threshold,
                'ks_statistic': ks_test['statistic'],
                'ks_p_value': ks_test['p_value'],
                'ks_significant': ks_test['significant'],
                'baseline_mean': float(baseline_mean),
                'current_mean': float(current_mean),
                'mean_shift': float(mean_shift),
                'mean_shift_pct': float(mean_shift_pct),
                'baseline_std': float(baseline_std),
                'current_std': float(current_std),
                'std_shift': float(std_shift),
                'std_shift_pct': float(std_shift_pct),
                'has_drift': has_drift,
                'drift_severity': drift_severity
            }

        return drift_results

    def compare_performance(
        self,
        baseline_metrics: Dict[str, float],
        current_metrics: Dict[str, float]
    ) -> Dict[str, Dict]:
        """
        Compare model performance metrics between baseline and current

        Args:
            baseline_metrics: Dictionary with baseline metrics (accuracy, precision, recall, f1)
            current_metrics: Dictionary with current metrics

        Returns:
            Dictionary with performance comparison and alerts
        """
        comparison = {}

        for metric_name in ['accuracy', 'precision', 'recall', 'f1']:
            if metric_name not in baseline_metrics or metric_name not in current_metrics:
                continue

            baseline_value = baseline_metrics[metric_name]
            current_value = current_metrics[metric_name]

            # Calculate degradation
            degradation = baseline_value - current_value
            degradation_pct = (degradation / baseline_value * 100) if baseline_value > 0 else 0

            # Determine alert level
            alert_level = 'none'
            if metric_name == 'accuracy':
                # Thresholds are in absolute values (0.05 = 5% absolute), convert to percentage
                # For 0.95 baseline, 0.05 degradation = 5.26% relative
                # We want to check if degradation_pct >= 5% (relative)
                # So we compare degradation_pct with threshold * 100
                if degradation_pct >= (self.accuracy_critical_threshold * 100):
                    alert_level = 'critical'
                elif degradation_pct >= (self.accuracy_degradation_threshold * 100):
                    alert_level = 'warning'
            else:
                # For other metrics, use 10% degradation as threshold
                if degradation_pct >= 10:
                    alert_level = 'critical'
                elif degradation_pct >= 5:
                    alert_level = 'warning'

            comparison[metric_name] = {
                'baseline': float(baseline_value),
                'current': float(current_value),
                'degradation': float(degradation),
                'degradation_pct': float(degradation_pct),
                'alert_level': alert_level
            }

        return comparison

    def detect_drift(
        self,
        baseline_data: pd.DataFrame,
        current_data: pd.DataFrame,
        baseline_metrics: Dict[str, float],
        current_metrics: Dict[str, float],
        numeric_columns: Optional[List[str]] = None
    ) -> Dict:
        """
        Complete drift detection: features + performance

        Args:
            baseline_data: Baseline dataset
            current_data: Current dataset
            baseline_metrics: Baseline performance metrics
            current_metrics: Current performance metrics
            numeric_columns: List of numeric columns to analyze

        Returns:
            Complete drift detection report
        """
        logger.info("Starting drift detection...")

        # Feature drift
        feature_drift = self.calculate_feature_drift(
            baseline_data, current_data, numeric_columns
        )

        # Performance drift
        performance_drift = self.compare_performance(baseline_metrics, current_metrics)

        # Generate alerts
        alerts = self._generate_alerts(feature_drift, performance_drift)

        # Summary
        total_features_with_drift = sum(1 for v in feature_drift.values() if v['has_drift'])
        total_alerts = len([a for a in alerts if a['level'] in ['warning', 'critical']])

        report = {
            'feature_drift': feature_drift,
            'performance_drift': performance_drift,
            'alerts': alerts,
            'summary': {
                'total_features_analyzed': len(feature_drift),
                'features_with_drift': total_features_with_drift,
                'total_alerts': total_alerts,
                'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['level'] == 'warning'])
            }
        }

        logger.info(f"Drift detection complete. Found {total_features_with_drift} features with drift, {total_alerts} alerts")

        return report

    def _generate_alerts(
        self,
        feature_drift: Dict,
        performance_drift: Dict
    ) -> List[Dict]:
        """
        Generate alerts based on drift detection results

        Args:
            feature_drift: Feature drift results
            performance_drift: Performance drift results

        Returns:
            List of alert dictionaries
        """
        alerts = []

        # Feature drift alerts
        for feature, metrics in feature_drift.items():
            if metrics['psi_alert']:
                alerts.append({
                    'type': 'feature_drift',
                    'feature': feature,
                    'level': 'critical' if metrics['psi'] > 0.5 else 'warning',
                    'message': f"Feature '{feature}' shows significant drift (PSI: {metrics['psi']:.3f})",
                    'psi': metrics['psi'],
                    'mean_shift_pct': metrics['mean_shift_pct']
                })
            elif metrics['ks_significant']:
                alerts.append({
                    'type': 'feature_drift',
                    'feature': feature,
                    'level': 'warning',
                    'message': f"Feature '{feature}' distribution changed significantly (KS p-value: {metrics['ks_p_value']:.4f})",
                    'ks_p_value': metrics['ks_p_value']
                })

        # Performance drift alerts
        for metric_name, metrics in performance_drift.items():
            if metrics['alert_level'] == 'critical':
                alerts.append({
                    'type': 'performance_degradation',
                    'metric': metric_name,
                    'level': 'critical',
                    'message': f"Critical degradation in {metric_name}: {metrics['degradation_pct']:.2f}% drop",
                    'degradation_pct': metrics['degradation_pct'],
                    'baseline': metrics['baseline'],
                    'current': metrics['current']
                })
            elif metrics['alert_level'] == 'warning':
                alerts.append({
                    'type': 'performance_degradation',
                    'metric': metric_name,
                    'level': 'warning',
                    'message': f"Warning: {metric_name} degraded by {metrics['degradation_pct']:.2f}%",
                    'degradation_pct': metrics['degradation_pct'],
                    'baseline': metrics['baseline'],
                    'current': metrics['current']
                })

        return alerts
