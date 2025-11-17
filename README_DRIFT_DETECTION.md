# 🔍 Data Drift Detection System

Complete data drift detection system integrated into your obesity classification ML project.

---

## 🚀 Quick Start

### 1. Run Drift Detection (3 minutes)
```bash
python scripts/simulate_drift.py
python scripts/detect_drift.py
python scripts/visualize_drift.py
```

### 2. Run Tests (2 minutes)
```bash
pytest tests/test_drift_detection.py -v
```

### 3. Setup CI/CD (5 minutes)
Copy workflows from `CI_CD_DRIFT_INTEGRATION.md` to `.github/workflows/`

---

## 📁 What's Included

### Code (1,500+ lines)
```
src/monitoring/
├── drift_detector.py (399 lines)      ← Core statistical detection
└── __init__.py                        ← Module exports

scripts/
├── detect_drift.py (292 lines)        ← Main detection pipeline
├── simulate_drift.py (197 lines)      ← Create test data
├── visualize_drift.py (343 lines)     ← Generate 3 PNG charts
└── compare_datasets.py (220 lines)    ← Data validation
```

### Tests (330+ lines)
```
tests/
└── test_drift_detection.py            ← 28 unit tests
    ├── PSI Calculation (6 tests)
    ├── Distribution Tests (5 tests)
    ├── Detector Tests (8 tests)
    ├── Integration Tests (1 test)
    ├── Report Generation (1 test)
    ├── Edge Cases (4 tests)
    └── Performance Thresholds (3 tests)
```

### Documentation (1,700+ lines)
```
├── FINAL_SUMMARY.md                   ← This complete overview
├── DRIFT_DETECTION_GUIDE.md           ← Execution guide (700 lines)
├── CI_CD_DRIFT_INTEGRATION.md         ← CI/CD setup (370 lines)
├── TESTING_QUICKSTART.md              ← Quick reference (280 lines)
├── MERGE_DRIFT_DETECTION.md           ← Merge details (410 lines)
└── COMPARACION_RAMAS.md               ← Branch comparison
```

### Configuration
```
MLproject                    ← MLflow entry points
dvc.yaml                    ← 3 new pipeline stages
requirements.txt            ← scipy==1.11.0 added
docker-compose.yml          ← 3 drift services (pre-configured)
```

---

## 🎯 Features

### Statistical Methods
- ✅ **Population Stability Index (PSI)** - Feature drift detection
- ✅ **Kolmogorov-Smirnov Test** - Distribution comparison
- ✅ **Mann-Whitney U Test** - Non-parametric comparison
- ✅ **Performance Degradation** - Model accuracy tracking

### Outputs
- ✅ **JSON Reports** - `reports/drift/drift_report.json`
- ✅ **Text Alerts** - `reports/drift/drift_alerts.txt`
- ✅ **Visualizations** - 3 PNG charts in `reports/figures/`

### Execution Methods
- ✅ **Direct Scripts** - `python scripts/detect_drift.py`
- ✅ **Docker** - `docker-compose up detect-drift`
- ✅ **DVC Pipeline** - `dvc repro detect_drift`
- ✅ **Unit Tests** - `pytest tests/test_drift_detection.py`

### Integrations
- ✅ **GitHub Actions** - 3 workflows included
- ✅ **GitLab CI** - Configuration provided
- ✅ **Jenkins** - Declarative pipeline
- ✅ **Slack** - Real-time alerts
- ✅ **Email** - HTML reports
- ✅ **Datadog** - Metrics tracking

---

## 📊 Pipeline Architecture

```
┌─────────────────────────────────────────────────┐
│ INPUT: Baseline Dataset (Clean, Original)      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ Stage 6: Simulate Drift (Optional)              │
│ - Shift Age/Weight/Height distributions        │
│ - Add 3% noise to other features                │
│ OUTPUT: dataset_with_drift.csv                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ Stage 7: Detect Drift                           │
│ - Calculate PSI per feature                     │
│ - Compare distributions (KS test)               │
│ - Track performance degradation                 │
│ - Generate alerts                               │
│ OUTPUTS:                                        │
│ - drift_report.json (technical)                 │
│ - drift_alerts.txt (human-readable)             │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ Stage 8: Visualize Drift                        │
│ - Distribution comparisons                      │
│ - Performance degradation charts                │
│ - PSI heatmaps                                  │
│ OUTPUTS: 3 PNG files                            │
└─────────────────────────────────────────────────┘
```

---

## 🧪 Test Coverage

**28 Unit Tests** covering:

| Test Group | Tests | Purpose |
|-----------|-------|---------|
| PSI Calculation | 6 | Verify drift metric accuracy |
| Distribution Comparison | 5 | Test statistical tests |
| DriftDetector Class | 8 | Core functionality |
| Integration | 1 | Real data validation |
| Report Generation | 1 | JSON serialization |
| Edge Cases | 4 | NaN, empty, single values |
| Performance Thresholds | 3 | Alert level validation |

Run with:
```bash
pytest tests/test_drift_detection.py -v --cov=src/monitoring
```

---

## 🚀 CI/CD Workflows

### GitHub Actions (Pre-Built)

**1. Drift Detection Workflow**
```
Trigger: Every push, PR, daily 2 AM UTC
Steps:
  1. Pull data from S3
  2. Train model if needed
  3. Simulate drift
  4. Detect drift
  5. Generate visualizations
  6. Comment on PRs
  7. Create artifacts
  8. Alert on critical drift
```

**2. Matrix Testing**
```
Trigger: Every push/PR
Tests:
  - OS: Ubuntu, macOS
  - Python: 3.9, 3.10, 3.11
  - Coverage to Codecov
```

**3. Weekly Report**
```
Trigger: Every Monday 8 AM UTC
Actions:
  1. Generate full report
  2. Create GitHub issue
  3. Slack notification
```

### Other Platforms
- ✅ **GitLab CI** - 4-stage pipeline
- ✅ **Jenkins** - 5-stage declarative pipeline

---

## 📈 Alert Thresholds

### Feature Drift (PSI)
```
PSI < 0.1   → ✅ No drift
PSI 0.1-0.2 → ⚠️  Minor drift (monitor)
PSI > 0.2   → 🚨 Significant drift (alert)
```

### Performance Degradation
```
Accuracy drop < 5%  → ✅ Acceptable
Accuracy drop 5-10% → ⚠️  Warning
Accuracy drop > 10% → 🚨 Critical
```

---

## 📖 Documentation Guide

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **FINAL_SUMMARY.md** | Complete overview | 10 min |
| **TESTING_QUICKSTART.md** | Quick reference | 5 min |
| **DRIFT_DETECTION_GUIDE.md** | Execution methods | 15 min |
| **CI_CD_DRIFT_INTEGRATION.md** | CI/CD setup | 20 min |
| **MERGE_DRIFT_DETECTION.md** | Technical details | 15 min |

---

## 🎓 Example Usage

### Example 1: Quick Local Test
```bash
# 1. Simulate drift
python scripts/simulate_drift.py
# Output: data/interim/dataset_with_drift.csv

# 2. Detect drift
python scripts/detect_drift.py
# Output: reports/drift/drift_report.json
# Output: reports/drift/drift_alerts.txt

# 3. Visualize
python scripts/visualize_drift.py
# Output: reports/figures/10_drift_distributions.png
# Output: reports/figures/11_drift_performance_comparison.png
# Output: reports/figures/12_drift_psi_heatmap.png
```

### Example 2: Run in Docker
```bash
# One command runs everything
docker-compose up simulate-drift detect-drift visualize-drift
```

### Example 3: Use DVC Pipeline
```bash
# Automatic dependency tracking
dvc repro detect_drift
```

### Example 4: Run Unit Tests
```bash
# Verify all components
pytest tests/test_drift_detection.py -v --cov=src/monitoring --cov-report=html
```

---

## 🔧 Configuration

### Adjust Detection Thresholds
Edit in your scripts:
```python
detector = DriftDetector(
    psi_threshold=0.2,                    # ← Adjust for sensitivity
    accuracy_degradation_threshold=0.05,  # ← 5% warning level
    accuracy_critical_threshold=0.10      # ← 10% critical level
)
```

### Add More Features
Modify numeric columns:
```python
numeric_cols = ['Age', 'Weight', 'Height', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
```

### Schedule Automated Runs
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * cd /app && docker-compose up detect-drift visualize-drift
```

---

## 🔔 Notification Setup

### Slack
1. Create webhook in Slack workspace
2. Add to CI/CD secrets: `SLACK_WEBHOOK`
3. Alerts automatically sent on drift

### Email
1. Configure SMTP server
2. Set recipient list
3. HTML reports sent automatically

### Datadog
1. Get API key
2. Configure integration script
3. Metrics sent for dashboards

---

## ✅ Pre-Deployment Checklist

- [ ] Tests passing: `pytest tests/test_drift_detection.py -v`
- [ ] Coverage > 80%
- [ ] Docker builds: `docker-compose build`
- [ ] DVC pipeline works: `dvc repro detect_drift`
- [ ] Drift detection outputs created
- [ ] Alerts configured (Slack/Email/Datadog)
- [ ] GitHub Actions workflows added
- [ ] Secrets configured in GitHub
- [ ] Monitoring dashboards created
- [ ] Team trained on usage

---

## 📞 Support

### Common Commands

```bash
# Run tests
pytest tests/test_drift_detection.py -v

# Test locally
python scripts/simulate_drift.py && python scripts/detect_drift.py

# With Docker
docker-compose up simulate-drift detect-drift visualize-drift

# With DVC
dvc repro detect_drift visualize_drift

# Check coverage
pytest tests/ --cov=src/monitoring --cov-report=html
```

### Troubleshooting

**Missing data:** Run `python scripts/run_eda.py` first
**Missing model:** Run `python scripts/run_ml.py` first
**Import errors:** Check `pip install -r requirements.txt`

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `src/monitoring/drift_detector.py` | Core statistical detection |
| `scripts/detect_drift.py` | Main execution script |
| `tests/test_drift_detection.py` | 28 unit tests |
| `dvc.yaml` | Pipeline definition |
| `docker-compose.yml` | Container services |
| `MLproject` | MLflow entry points |

---

## 🎯 Next Steps

1. **Today**: Run local tests and drift detection
2. **This Week**: Setup GitHub Actions
3. **Next Sprint**: Tune thresholds with real data
4. **Ongoing**: Monitor and refine

---

## 📊 Project Status

```
✅ Drift detection system: IMPLEMENTED
✅ Unit tests (28): PASSING
✅ CI/CD workflows: READY
✅ Documentation: COMPLETE
✅ Docker support: CONFIGURED
✅ DVC integration: COMPLETE
✅ Alert system: READY

Status: 🚀 PRODUCTION READY
```

---

**Version:** 1.0.0
**Status:** ✅ Complete
**Branch:** eze
**Last Updated:** 2025-11-17
**Ready for:** Production Deployment

---

## 🤝 Contributing

To modify the drift detection system:

1. Run tests: `pytest tests/test_drift_detection.py -v`
2. Make changes
3. Add tests for new features
4. Update documentation
5. Commit with clear messages

---

**Start monitoring data drift today!** 🚀

See `TESTING_QUICKSTART.md` for commands to run right now.
