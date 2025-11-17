# 🧪 Drift Detection Testing Quick Start

Fast reference for running tests and setting up CI/CD.

---

## 🎯 Quick Commands

### Run All Tests
```bash
# Run all drift detection tests
pytest tests/test_drift_detection.py -v

# With coverage report
pytest tests/test_drift_detection.py -v --cov=src/monitoring --cov-report=html

# Run specific test class
pytest tests/test_drift_detection.py::TestPSICalculation -v

# Run specific test
pytest tests/test_drift_detection.py::TestPSICalculation::test_psi_no_drift -v
```

### Run Drift Detection
```bash
# Sequential execution
python scripts/simulate_drift.py
python scripts/detect_drift.py
python scripts/visualize_drift.py

# Docker
docker-compose up simulate-drift detect-drift visualize-drift

# DVC
dvc repro detect_drift
```

---

## 📊 Test Coverage

**28 Unit Tests** covering:

| Category | Tests | Purpose |
|----------|-------|---------|
| PSI Calculation | 6 | Verify drift metrics accuracy |
| Distribution Comparison | 5 | Test statistical tests (KS, Mann-Whitney) |
| DriftDetector Class | 8 | Core drift detection functionality |
| Integration | 1 | Real data testing |
| Report Generation | 1 | JSON serialization |
| Edge Cases | 4 | NaN, empty data, single values |
| Performance Thresholds | 3 | Alert level validation |

---

## 🚀 CI/CD Setup (5 minutes)

### GitHub Actions

1. **Create workflows directory:**
```bash
mkdir -p .github/workflows
```

2. **Copy drift-detection.yml:**
See `CI_CD_DRIFT_INTEGRATION.md` → GitHub Actions section

3. **Set secrets:**
```bash
# In GitHub UI: Settings → Secrets → Add:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SLACK_WEBHOOK (optional)
```

4. **Push to trigger:**
```bash
git push origin main
```

That's it! ✅ Workflow runs automatically.

---

### GitLab CI

1. **Copy .gitlab-ci.yml to project root:**
See `CI_CD_DRIFT_INTEGRATION.md` → GitLab CI section

2. **Push to trigger:**
```bash
git push origin main
```

---

### Jenkins

1. **Create new Pipeline job**
2. **Copy Jenkinsfile content** to pipeline definition
3. **Configure triggers:** GitHub push, daily at 2 AM
4. **Add credentials:** AWS keys, Slack webhook

---

## ✅ Test Examples

### Test PSI Calculation
```python
from src.monitoring.drift_detector import calculate_psi
import pandas as pd
import numpy as np

# No drift
baseline = pd.Series(np.random.normal(0, 1, 1000))
psi = calculate_psi(baseline, baseline)
assert psi < 0.1  # ✅ Pass

# Major drift
drifted = pd.Series(np.random.normal(1, 1, 1000))
psi = calculate_psi(baseline, drifted)
assert psi > 0.2  # ✅ Pass
```

### Test Drift Detection
```python
from src.monitoring.drift_detector import DriftDetector

detector = DriftDetector()

# Create test data
baseline = pd.DataFrame({
    'Age': [20, 30, 40, 50, 60],
    'Weight': [60, 70, 80, 90, 100]
})

drifted = baseline.copy()
drifted['Age'] = drifted['Age'] + 5  # Add drift

# Run detection
report = detector.detect_drift(
    baseline, drifted,
    {'accuracy': 0.99, 'precision': 0.99, 'recall': 0.99, 'f1': 0.99},
    {'accuracy': 0.85, 'precision': 0.85, 'recall': 0.85, 'f1': 0.85}
)

# Verify
assert len(report['alerts']) > 0  # ✅ Drift detected
```

---

## 📋 Pre-deployment Checklist

- [ ] All tests passing: `pytest tests/ -v`
- [ ] Coverage > 80%: `pytest --cov=src/monitoring`
- [ ] Drift detection works: `python scripts/detect_drift.py`
- [ ] Reports generated: Check `reports/drift/` and `reports/figures/`
- [ ] Docker builds: `docker-compose build`
- [ ] DVC pipeline: `dvc repro detect_drift`
- [ ] CI/CD secrets configured
- [ ] Notifications working (Slack/Email)

---

## 🔍 Troubleshooting Tests

### Missing Dependencies
```bash
pip install pytest pytest-cov numpy pandas scipy scikit-learn
```

### Import Errors
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_drift_detection.py -v
```

### Test Timeout
```bash
# Set longer timeout
pytest tests/test_drift_detection.py -v --timeout=60
```

---

## 📊 Expected Test Output

```
tests/test_drift_detection.py::TestPSICalculation::test_psi_no_drift PASSED        [  3%]
tests/test_drift_detection.py::TestPSICalculation::test_psi_minor_drift PASSED      [  7%]
tests/test_drift_detection.py::TestPSICalculation::test_psi_major_drift PASSED      [ 10%]
tests/test_drift_detection.py::TestPSICalculation::test_psi_with_nan PASSED         [ 14%]
tests/test_drift_detection.py::TestPSICalculation::test_psi_empty_series PASSED     [ 17%]
tests/test_drift_detection.py::TestPSICalculation::test_psi_single_value PASSED     [ 21%]
...
=============================== 28 passed in 2.34s ===============================
```

---

## 🎯 Common Scenarios

### Scenario 1: Test locally before pushing
```bash
# Run tests
pytest tests/test_drift_detection.py -v

# Test drift on real data
python scripts/simulate_drift.py
python scripts/detect_drift.py

# Push if all pass
git push origin feature-branch
```

### Scenario 2: Fix failing test
```bash
# Run single test
pytest tests/test_drift_detection.py::TestClass::test_name -v

# Edit code
# Re-run
pytest tests/test_drift_detection.py::TestClass::test_name -v
```

### Scenario 3: Setup CI/CD
```bash
# 1. Add GitHub Actions
cp CI_CD_DRIFT_INTEGRATION.md .github/workflows/drift-detection.yml

# 2. Set secrets in GitHub UI
# 3. Push and trigger workflow
git push origin main
```

---

## 📚 Full Documentation

- **Tests Details:** `tests/test_drift_detection.py`
- **Execution Guide:** `DRIFT_DETECTION_GUIDE.md`
- **CI/CD Setup:** `CI_CD_DRIFT_INTEGRATION.md`
- **Merge Details:** `MERGE_DRIFT_DETECTION.md`
- **Branch Comparison:** `COMPARACION_RAMAS.md`

---

## 💡 Tips

1. **Run tests before every push:**
   ```bash
   pytest tests/test_drift_detection.py -v
   ```

2. **Watch coverage:**
   ```bash
   pytest tests/test_drift_detection.py --cov=src/monitoring --cov-report=term-missing
   ```

3. **Run in Docker:**
   ```bash
   docker-compose run --rm ml-pipeline pytest tests/test_drift_detection.py -v
   ```

4. **Continuous testing:**
   ```bash
   pytest-watch tests/test_drift_detection.py
   ```

---

**Ready to test!** 🚀

Start with:
```bash
pytest tests/test_drift_detection.py -v
```
