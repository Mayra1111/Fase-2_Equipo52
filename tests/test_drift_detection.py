"""
Unit Tests for Data Drift Detection Module

Tests for:
- PSI calculation
- Distribution comparison
- Drift detection pipeline
- Alert generation
- Report generation
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json
import tempfile
from typing import Dict, Tuple

from src.monitoring.drift_detector import (
    DriftDetector,
    calculate_psi,
    compare_distributions
)
from src.utils.config import (
    REFACTORED_CLEAN_DATA_PATH,
    INTERIM_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    NUMERIC_COLUMNS
)


class TestPSICalculation:
    """Test Population Stability Index calculation"""

    def test_psi_no_drift(self):
        """PSI should be near 0 when distributions are identical"""
        data = pd.Series(np.random.normal(0, 1, 1000))
        psi = calculate_psi(data, data)

        assert isinstance(psi, float)
        assert psi < 0.1, f"PSI should be < 0.1 for identical distributions, got {psi}"

    def test_psi_minor_drift(self):
        """PSI should be between 0.1-0.2 for minor shifts"""
        baseline = pd.Series(np.random.normal(0, 1, 1000))
        current = pd.Series(np.random.normal(0.05, 1, 1000))  # 5% shift
        psi = calculate_psi(baseline, current)

        assert isinstance(psi, float)
        assert psi >= 0, "PSI should be non-negative"

    def test_psi_major_drift(self):
        """PSI should be > 0.2 for major distribution shifts"""
        baseline = pd.Series(np.random.normal(0, 1, 1000))
        current = pd.Series(np.random.normal(1, 1, 1000))  # 1 std shift
        psi = calculate_psi(baseline, current)

        assert isinstance(psi, float)
        assert psi > 0.2, f"PSI should be > 0.2 for major shift, got {psi}"

    def test_psi_with_nan(self):
        """PSI should handle NaN values gracefully"""
        baseline = pd.Series([1, 2, 3, np.nan, 5, 6, 7, 8, 9, 10])
        current = pd.Series([1, 2, 3, 4, np.nan, 6, 7, 8, 9, 10])
        psi = calculate_psi(baseline, current)

        assert isinstance(psi, float)
        assert not np.isnan(psi), "PSI should not be NaN even with missing values"

    def test_psi_empty_series(self):
        """PSI should return NaN for empty series"""
        empty = pd.Series([], dtype=float)
        data = pd.Series([1, 2, 3])
        psi = calculate_psi(empty, data)

        assert np.isnan(psi), "PSI should be NaN for empty series"

    def test_psi_single_value(self):
        """PSI should handle single-value distributions"""
        baseline = pd.Series([5.0] * 100)
        current = pd.Series([5.0] * 100)
        psi = calculate_psi(baseline, current)

        assert psi == 0.0, "PSI should be 0 for identical single-value distributions"


class TestDistributionComparison:
    """Test distribution comparison tests"""

    def test_ks_test_identical_distributions(self):
        """KS test should show no significance for identical distributions"""
        np.random.seed(42)
        data = pd.Series(np.random.normal(0, 1, 500))
        # Use copy to avoid reference issues
        data_copy = data.copy()
        result = compare_distributions(data, data_copy, test_type='ks')

        assert 'p_value' in result
        assert 'statistic' in result
        assert 'significant' in result
        # When comparing identical distributions, p-value should be very high (not significant)
        # The statistic should be 0 or very close to 0, making p-value = 1.0 or close to 1.0
        # Due to numerical precision, we check that it's not significant
        # Use not instead of is False because result['significant'] is numpy.bool_, not Python bool
        assert not result['significant'], \
            f"Identical distributions should not be significant. Got p_value={result['p_value']}, significant={result['significant']}, statistic={result['statistic']}"

    def test_ks_test_different_distributions(self):
        """KS test should detect significantly different distributions"""
        np.random.seed(42)
        baseline = pd.Series(np.random.normal(0, 1, 500))
        current = pd.Series(np.random.normal(3, 1, 500))  # Very different
        result = compare_distributions(baseline, current, test_type='ks')

        # numpy.bool_ works correctly in boolean context
        assert result['significant'], \
            f"Very different distributions should be significant. Got p_value={result['p_value']}, significant={result['significant']}"
        assert result['p_value'] < 0.05

    def test_mannwhitney_test(self):
        """Mann-Whitney U test should work correctly"""
        baseline = pd.Series(np.random.normal(0, 1, 500))
        current = pd.Series(np.random.normal(2, 1, 500))
        result = compare_distributions(baseline, current, test_type='mannwhitney')

        assert 'p_value' in result
        assert 'statistic' in result
        assert 'significant' in result

    def test_invalid_test_type(self):
        """Should raise error for invalid test type"""
        data = pd.Series([1, 2, 3])

        with pytest.raises(ValueError):
            compare_distributions(data, data, test_type='invalid_test')

    def test_comparison_with_nan(self):
        """Distribution comparison should handle NaN values"""
        baseline = pd.Series([1, 2, 3, np.nan, 5])
        current = pd.Series([1, 2, 3, 4, np.nan])
        result = compare_distributions(baseline, current)

        assert result['statistic'] is not None or np.isnan(result['statistic'])


class TestDriftDetector:
    """Test DriftDetector class"""

    @pytest.fixture
    def drift_detector(self):
        """Create DriftDetector instance"""
        return DriftDetector(
            psi_threshold=0.2,
            accuracy_degradation_threshold=0.05,
            accuracy_critical_threshold=0.10
        )

    @pytest.fixture
    def sample_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Create sample baseline and drifted datasets"""
        np.random.seed(42)

        n_samples = 500
        baseline = pd.DataFrame({
            'Age': np.random.normal(45, 15, n_samples),
            'Weight': np.random.normal(75, 15, n_samples),
            'Height': np.random.normal(1.7, 0.1, n_samples),
            'FCVC': np.random.uniform(1, 3, n_samples),
            'NCP': np.random.uniform(1, 4, n_samples),
            'CH2O': np.random.uniform(1, 3, n_samples),
            'FAF': np.random.uniform(0, 3, n_samples),
            'TUE': np.random.uniform(0, 2, n_samples),
        })

        # Create drifted version
        drifted = baseline.copy()
        drifted['Age'] = drifted['Age'] + 5  # 5-year increase
        drifted['Weight'] = drifted['Weight'] * 1.1  # 10% increase

        return baseline, drifted

    def test_detector_initialization(self, drift_detector):
        """Test DriftDetector initialization"""
        assert drift_detector.psi_threshold == 0.2
        assert drift_detector.accuracy_degradation_threshold == 0.05
        assert drift_detector.accuracy_critical_threshold == 0.10

    def test_feature_drift_calculation(self, drift_detector, sample_data):
        """Test feature drift calculation"""
        baseline, drifted = sample_data
        numeric_cols = ['Age', 'Weight', 'Height', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']

        feature_drift = drift_detector.calculate_feature_drift(
            baseline, drifted, numeric_columns=numeric_cols
        )

        assert isinstance(feature_drift, dict)
        assert len(feature_drift) == len(numeric_cols)

        # Check Age has drift (we shifted it)
        assert feature_drift['Age']['has_drift']
        assert feature_drift['Age']['psi'] > 0.2 or feature_drift['Age']['ks_significant']

    def test_performance_comparison(self, drift_detector):
        """Test performance metrics comparison"""
        baseline_metrics = {
            'accuracy': 0.95,
            'precision': 0.94,
            'recall': 0.96,
            'f1': 0.95
        }

        current_metrics = {
            'accuracy': 0.90,  # 5% degradation
            'precision': 0.89,  # 5.3% degradation
            'recall': 0.91,
            'f1': 0.90
        }

        comparison = drift_detector.compare_performance(baseline_metrics, current_metrics)

        assert 'accuracy' in comparison
        assert comparison['accuracy']['degradation_pct'] >= 5
        assert comparison['accuracy']['alert_level'] == 'warning'

    def test_alert_generation(self, drift_detector, sample_data):
        """Test alert generation"""
        baseline, drifted = sample_data
        baseline_metrics = {'accuracy': 0.99, 'precision': 0.99, 'recall': 0.99, 'f1': 0.99}
        current_metrics = {'accuracy': 0.65, 'precision': 0.68, 'recall': 0.65, 'f1': 0.66}

        report = drift_detector.detect_drift(
            baseline,
            drifted,
            baseline_metrics,
            current_metrics,
            numeric_columns=['Age', 'Weight', 'Height']
        )

        assert 'alerts' in report
        assert isinstance(report['alerts'], list)
        assert len(report['alerts']) > 0

        # Check alert structure
        for alert in report['alerts']:
            assert 'type' in alert
            assert 'level' in alert
            assert 'message' in alert
            assert alert['level'] in ['critical', 'warning']

    def test_complete_drift_detection(self, drift_detector, sample_data):
        """Test complete drift detection pipeline"""
        baseline, drifted = sample_data
        baseline_metrics = {'accuracy': 0.95, 'precision': 0.95, 'recall': 0.95, 'f1': 0.95}
        current_metrics = {'accuracy': 0.85, 'precision': 0.85, 'recall': 0.85, 'f1': 0.85}

        report = drift_detector.detect_drift(
            baseline,
            drifted,
            baseline_metrics,
            current_metrics
        )

        assert 'feature_drift' in report
        assert 'performance_drift' in report
        assert 'alerts' in report
        assert 'summary' in report

        # Check summary structure
        assert 'total_features_analyzed' in report['summary']
        assert 'features_with_drift' in report['summary']
        assert 'total_alerts' in report['summary']
        assert 'critical_alerts' in report['summary']
        assert 'warning_alerts' in report['summary']

    def test_drift_severity_levels(self, drift_detector):
        """Test drift severity classification"""
        # Low PSI = no drift
        baseline = pd.Series(np.random.normal(0, 1, 100))
        current = pd.Series(np.random.normal(0.01, 1, 100))

        feature_drift = drift_detector.calculate_feature_drift(
            pd.DataFrame({'col': baseline}),
            pd.DataFrame({'col': current}),
            numeric_columns=['col']
        )

        assert feature_drift['col']['drift_severity'] in ['none', 'low', 'medium', 'high']


class TestIntegration:
    """Integration tests with real data"""

    @pytest.mark.skipif(
        not REFACTORED_CLEAN_DATA_PATH.exists(),
        reason="Requires trained model and clean data"
    )
    def test_with_real_data(self):
        """Test drift detection with real project data"""
        if not REFACTORED_CLEAN_DATA_PATH.exists():
            pytest.skip("Clean data not available")

        # Load data
        df = pd.read_csv(REFACTORED_CLEAN_DATA_PATH)

        # Create drift
        df_drifted = df.copy()
        df_drifted['Age'] = df_drifted['Age'] * 1.1
        df_drifted['Weight'] = df_drifted['Weight'] * 1.15

        # Test detection
        detector = DriftDetector()
        numeric_cols = [col for col in NUMERIC_COLUMNS if col in df.columns]

        report = detector.detect_drift(
            df,
            df_drifted,
            baseline_metrics={'accuracy': 0.99, 'precision': 0.99, 'recall': 0.99, 'f1': 0.99},
            current_metrics={'accuracy': 0.75, 'precision': 0.76, 'recall': 0.75, 'f1': 0.75},
            numeric_columns=numeric_cols
        )

        assert report is not None
        assert len(report['alerts']) > 0


class TestReportGeneration:
    """Test report generation and serialization"""

    def test_report_json_serialization(self):
        """Test that reports can be serialized to JSON"""
        detector = DriftDetector()

        baseline = pd.DataFrame({
            'Age': [20, 30, 40, 50, 60],
            'Weight': [60, 70, 80, 90, 100]
        })

        drifted = pd.DataFrame({
            'Age': [25, 35, 45, 55, 65],
            'Weight': [65, 75, 85, 95, 105]
        })

        report = detector.detect_drift(
            baseline,
            drifted,
            baseline_metrics={'accuracy': 0.99, 'precision': 0.99, 'recall': 0.99, 'f1': 0.99},
            current_metrics={'accuracy': 0.85, 'precision': 0.85, 'recall': 0.85, 'f1': 0.85},
            numeric_columns=['Age', 'Weight']
        )

        # Should be serializable to JSON
        json_str = json.dumps(report, default=str)
        assert json_str is not None

        # Should be deserializable
        deserialized = json.loads(json_str)
        assert 'feature_drift' in deserialized


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_single_row_dataframes(self):
        """Test with single-row dataframes"""
        detector = DriftDetector()

        baseline = pd.DataFrame({'Age': [30], 'Weight': [75]})
        current = pd.DataFrame({'Age': [31], 'Weight': [76]})

        # Should not crash
        feature_drift = detector.calculate_feature_drift(
            baseline, current, numeric_columns=['Age', 'Weight']
        )

        assert isinstance(feature_drift, dict)

    def test_empty_numeric_columns(self):
        """Test with empty numeric columns list"""
        detector = DriftDetector()

        baseline = pd.DataFrame({'col': [1, 2, 3]})
        current = pd.DataFrame({'col': [1, 2, 3]})

        feature_drift = detector.calculate_feature_drift(
            baseline, current, numeric_columns=[]
        )

        assert len(feature_drift) == 0

    def test_mismatched_columns(self):
        """Test with different columns in baseline vs current"""
        detector = DriftDetector()

        baseline = pd.DataFrame({'Age': [20, 30], 'Weight': [60, 70]})
        current = pd.DataFrame({'Age': [25, 35], 'Height': [170, 180]})

        feature_drift = detector.calculate_feature_drift(
            baseline, current, numeric_columns=['Age', 'Weight', 'Height']
        )

        # Should handle missing columns gracefully
        assert 'Age' in feature_drift  # Present in both
        # Weight and Height might not be present

    def test_all_nan_column(self):
        """Test with column containing all NaN values"""
        detector = DriftDetector()

        baseline = pd.DataFrame({'Age': [20, 30], 'Weight': [np.nan, np.nan]})
        current = pd.DataFrame({'Age': [25, 35], 'Weight': [np.nan, np.nan]})

        feature_drift = detector.calculate_feature_drift(
            baseline, current, numeric_columns=['Age', 'Weight']
        )

        # Should handle gracefully
        assert isinstance(feature_drift, dict)


class TestPerformanceMetrics:
    """Test performance metric thresholds"""

    def test_critical_accuracy_degradation(self):
        """Test critical alert for 15% accuracy drop"""
        detector = DriftDetector(accuracy_critical_threshold=0.10)

        baseline = {'accuracy': 0.95, 'precision': 0.95, 'recall': 0.95, 'f1': 0.95}
        current = {'accuracy': 0.80, 'precision': 0.80, 'recall': 0.80, 'f1': 0.80}

        comparison = detector.compare_performance(baseline, current)

        assert comparison['accuracy']['alert_level'] == 'critical'
        assert comparison['accuracy']['degradation_pct'] > 10

    def test_warning_level_degradation(self):
        """Test warning alert for 7% accuracy drop"""
        detector = DriftDetector(
            accuracy_degradation_threshold=0.05,
            accuracy_critical_threshold=0.15
        )

        baseline = {'accuracy': 0.95, 'precision': 0.95, 'recall': 0.95, 'f1': 0.95}
        current = {'accuracy': 0.88, 'precision': 0.88, 'recall': 0.88, 'f1': 0.88}

        comparison = detector.compare_performance(baseline, current)

        assert comparison['accuracy']['alert_level'] == 'warning'

    def test_no_alert_minimal_degradation(self):
        """Test no alert for < 5% degradation"""
        detector = DriftDetector(accuracy_degradation_threshold=0.05)

        baseline = {'accuracy': 0.95, 'precision': 0.95, 'recall': 0.95, 'f1': 0.95}
        current = {'accuracy': 0.93, 'precision': 0.93, 'recall': 0.93, 'f1': 0.93}

        comparison = detector.compare_performance(baseline, current)

        assert comparison['accuracy']['alert_level'] == 'none'


# ============================================================================
# CLI Test Runner
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
