# 🔍 DVC Drift Detection Orchestration Guide

**Version**: 3.1
**Status**: ✅ Production Ready
**Date**: 2025-11-17

---

## Overview

Your ML pipeline now supports **three ways to run drift detection**:

1. **Full Pipeline + Drift** (Automated via DVC) - Complete end-to-end
2. **Drift-Only** (Automated via DVC) - Just drift detection on existing model
3. **Manual Drift Control** - Individual drift stages with manual coordination

---

## 🎯 Quick Reference

### Option 1: Full Pipeline including Drift (Recommended for Complete Runs)

```bash
docker-compose run dvc-full-pipeline
```

**What happens**:
- ✅ EDA (data exploration)
- ✅ Preprocess (feature engineering)
- ✅ Train (model training)
- ✅ Evaluate (model evaluation)
- ✅ Visualize (EDA visualizations)
- ✅ Simulate Drift (create drifted dataset)
- ✅ Detect Drift (compare baseline vs drifted)
- ✅ Visualize Drift (generate drift plots)

**Time**: 10-20 minutes (depends on data size)
**Output**: All reports, models, metrics, and drift analysis

---

### Option 2: Drift-Only Pipeline (Recommended for Monitoring)

```bash
docker-compose run dvc-drift-pipeline
```

**Requirements**:
- Trained model must exist in `models/`
- Baseline data must exist in `data/interim/`

**What happens**:
- ✅ Simulate Drift (create drifted dataset)
- ✅ Detect Drift (compare baseline vs drifted)
- ✅ Visualize Drift (generate drift plots)

**Time**: 2-5 minutes
**Output**: Drift reports, alerts, and visualizations

**Use case**:
- Production monitoring
- Regular drift checks on trained model
- CI/CD pipelines
- Automated monitoring jobs

---

### Option 3: Manual Drift Control (For Debugging)

```bash
# Step 1: Pull data
docker-compose run dvc-pull

# Step 2: Simulate drift
docker-compose run --profile drift-manual simulate-drift

# Step 3: Detect drift
docker-compose run --profile drift-manual detect-drift

# Step 4: Visualize drift
docker-compose run --profile drift-manual visualize-drift
```

**Use case**:
- Debugging drift detection issues
- Testing individual stages
- Understanding each step in detail

---

## 📊 Detailed Comparison

| Feature | Full Pipeline | Drift-Only | Manual |
|---------|---------------|-----------|--------|
| **Runs ML Pipeline** | ✅ Yes | ❌ No | ❌ No |
| **Requires Trained Model** | ❌ No | ✅ Yes | ✅ Yes |
| **Automated Orchestration** | ✅ DVC | ✅ DVC | ❌ Manual |
| **Time to Complete** | 10-20 min | 2-5 min | 5-10 min |
| **Single Command** | ✅ Yes | ✅ Yes | ❌ No (3 commands) |
| **Good for Development** | ✅ Yes | ⚠️ Partial | ✅ Yes |
| **Good for Production** | ✅ Yes | ✅ Yes | ❌ No |
| **Good for CI/CD** | ✅ Yes | ✅ Yes | ⚠️ Manual |
| **Dependency Management** | ✅ Automatic | ✅ Automatic | ⚠️ Manual |

---

## 🔄 DVC Pipeline Stages

Your `dvc.yaml` defines 8 stages:

```
Stage 1: eda              (Exploratory Data Analysis)
  ↓
Stage 2: preprocess       (Feature Engineering)
  ↓
Stage 3: train            (Model Training)
  ↓
Stage 4: evaluate         (Model Evaluation)
  ↓
Stage 5: visualize        (EDA Visualizations)
  ↓
Stage 6: simulate_drift   (Create Drifted Data)
  ↓
Stage 7: detect_drift     (Detect Drift)
  ↓
Stage 8: visualize_drift  (Drift Visualizations)
```

**DVC Automatically**:
- ✅ Runs stages in correct order
- ✅ Detects which stages need rerunning
- ✅ Caches outputs
- ✅ Skips stages with unchanged inputs

---

## 🚀 Usage Examples

### Example 1: Production Full Run

```bash
# Complete pipeline run in production
docker-compose run dvc-full-pipeline

# Output includes:
# ✅ Trained model (models/best_pipeline.joblib)
# ✅ Model metadata (models/model_metadata.joblib)
# ✅ Evaluation metrics (reports/metrics/evaluation_metrics.json)
# ✅ EDA plots (reports/figures/01_*.png)
# ✅ Drift simulation (data/interim/dataset_with_drift.csv)
# ✅ Drift metrics (reports/drift/drift_report.json)
# ✅ Drift alerts (reports/drift/drift_alerts.txt)
# ✅ Drift plots (reports/figures/10_*.png)
```

---

### Example 2: Daily Monitoring Run

```bash
# Quick drift check on existing model
docker-compose run dvc-drift-pipeline

# Output includes:
# ✅ Drift report (reports/drift/drift_report.json)
# ✅ Alerts (reports/drift/drift_alerts.txt)
# ✅ Visualizations (reports/figures/10_*.png)
# Time: ~3 minutes
```

---

### Example 3: Debugging Drift Detection

```bash
# Step through each drift stage manually
docker-compose run dvc-pull

# Examine intermediate outputs
ls -la data/interim/

# Simulate drift
docker-compose run --profile drift-manual simulate-drift
cat reports/drift/

# Detect drift
docker-compose run --profile drift-manual detect-drift
cat reports/drift/drift_report.json

# Visualize drift
docker-compose run --profile drift-manual visualize-drift
ls -la reports/figures/10_*
```

---

### Example 4: CI/CD Pipeline

```yaml
# GitHub Actions example
name: ML Pipeline with Drift Detection

on: [push, schedule]

jobs:
  ml-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run full ML pipeline with drift detection
        run: docker-compose run dvc-full-pipeline

      - name: Upload metrics
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: ml-metrics
          path: reports/
```

---

## 📋 DVC Commands Reference

### View Pipeline Structure

```bash
docker-compose run shell
# Inside container:
$ dvc dag          # View pipeline DAG
$ dvc status       # Check status
$ dvc params diff  # Compare parameters
```

### Run Specific Stages

```bash
# Run single stage and dependencies
docker-compose run shell dvc repro --single-item train

# Run from stage to final
docker-compose run shell dvc repro --single-item visualize_drift
```

### Force Rerun

```bash
# Rerun pipeline ignoring cache
docker-compose run shell dvc repro --force

# Rerun specific stage
docker-compose run shell dvc repro --force --single-item detect_drift
```

### View Outputs

```bash
# Check what was produced
docker-compose run shell dvc dag --outs

# See output files
docker-compose run shell find . -name "*.json" -type f
```

---

## 🎯 Choosing the Right Option

### Use **dvc-full-pipeline** when:
- ✅ Building/updating the model
- ✅ Complete pipeline validation needed
- ✅ Testing entire workflow
- ✅ Production model updates
- ✅ Full reproducibility required

### Use **dvc-drift-pipeline** when:
- ✅ Model is already trained and deployed
- ✅ Monitoring for data drift
- ✅ Regular scheduled checks
- ✅ CI/CD drift detection jobs
- ✅ Quick feedback loop needed (~3 min)

### Use **Manual drift** when:
- ✅ Debugging individual stages
- ✅ Testing specific drift detector
- ✅ Educational purposes
- ✅ Understanding the flow
- ✅ Experimenting with parameters

---

## 📊 Drift Detection Output

### Files Generated

```
reports/
├── drift/
│   ├── drift_report.json          # Detailed drift metrics
│   └── drift_alerts.txt           # Human-readable alerts
└── figures/
    ├── 10_drift_distributions.png  # Feature distributions
    ├── 11_drift_performance_comparison.png  # Model performance
    └── 12_drift_psi_heatmap.png   # PSI heatmap
```

### Drift Report Format

```json
{
  "baseline_stats": {
    "timestamp": "2025-11-17T15:00:00",
    "dataset_size": 5000,
    "features": 13
  },
  "drift_stats": {
    "timestamp": "2025-11-17T15:05:00",
    "dataset_size": 5000
  },
  "drift_detection": {
    "features": [
      {
        "name": "Age",
        "psi": 0.042,
        "ks_statistic": 0.145,
        "mann_whitney_pvalue": 0.23,
        "drift_detected": false
      },
      ...
    ],
    "overall_drift": false
  }
}
```

---

## 🔧 Configuration

### Parameters for Drift Detection

Edit `config/params.yaml`:

```yaml
# Drift detection parameters
drift:
  psi_threshold: 0.25          # Population Stability Index threshold
  ks_threshold: 0.2            # Kolmogorov-Smirnov test threshold
  mann_whitney_threshold: 0.05  # Mann-Whitney U test p-value threshold

# Simulation parameters
simulation:
  noise_level: 0.03             # 3% noise in features
  shift_amount: 0.5             # 0.5 std shift for some features
```

---

## 🚨 Drift Detection Thresholds

| Metric | Purpose | Default | Range |
|--------|---------|---------|-------|
| **PSI** | Population Stability Index | 0.25 | 0.0-1.0 |
| **KS** | Kolmogorov-Smirnov Test | 0.2 | 0.0-1.0 |
| **Mann-Whitney** | Statistical Test p-value | 0.05 | 0.0-1.0 |

**Interpretation**:
- **Drift Detected**: Any feature crosses threshold
- **Alert Level**: Based on number of drifted features
- **Action**: Retrain model if drift detected

---

## 📈 Performance Tips

### Optimize Full Pipeline

```bash
# Run with specific parameters
docker-compose run dvc-full-pipeline dvc repro --no-commit
# Prevents DVC from committing results

# Run subset of stages
docker-compose run shell dvc repro --single-item visualize_drift
# Only runs stages up to visualize_drift
```

### Cache Management

```bash
# Clear DVC cache (free disk space)
docker-compose run shell dvc gc --workspace

# View cache status
docker-compose run shell du -sh .dvc/cache
```

---

## 🔐 Security & Credentials

### AWS S3 Configuration for DVC Remote

```bash
# .env file
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DVC_REMOTE_URL=s3://your-bucket/obesity-ml
DVC_REMOTE_NAME=myremote
```

The Dockerfile entrypoint automatically configures DVC remote using these variables.

---

## ✅ Verification Checklist

After first run:

- [ ] `models/best_pipeline.joblib` exists
- [ ] `reports/metrics/evaluation_metrics.json` exists
- [ ] `reports/drift/drift_report.json` exists
- [ ] `reports/figures/10_*.png` drift plots exist
- [ ] `reports/drift/drift_alerts.txt` has readable output
- [ ] All services exited with code 0

---

## 🆘 Troubleshooting

### Issue: "Dataset_with_drift.csv not found"

**Cause**: simulate_drift stage hasn't run
**Solution**:
```bash
docker-compose run dvc-full-pipeline  # Run full pipeline first
# OR
docker-compose run dvc-drift-pipeline # Run drift pipeline
```

### Issue: "Model not found"

**Cause**: train stage hasn't run
**Solution**:
```bash
# For drift-only, must train model first:
docker-compose run dvc-full-pipeline  # Train model
# Then run drift-only:
docker-compose run dvc-drift-pipeline # Check drift
```

### Issue: "DVC repro fails"

**Cause**: Missing dependencies or parameter changes
**Solution**:
```bash
docker-compose run shell dvc status   # Check what's wrong
docker-compose run shell dvc repro -v # Verbose output
```

---

## 📚 Next Steps

1. **Run full pipeline**: `docker-compose run dvc-full-pipeline`
2. **Check outputs**: `ls -la reports/ models/`
3. **Review drift report**: `cat reports/drift/drift_report.json`
4. **View visualizations**: Open `reports/figures/10_*.png`
5. **Setup monitoring**: Schedule `dvc-drift-pipeline` daily

---

## 📖 Related Documentation

- [HYBRID_DOCKER_GUIDE.md](HYBRID_DOCKER_GUIDE.md) - Complete Docker reference
- [QUICK_START_HYBRID.md](QUICK_START_HYBRID.md) - Quick start guide
- [README_DRIFT_DETECTION.md](README_DRIFT_DETECTION.md) - Drift detection details
- [dvc.yaml](dvc.yaml) - DVC pipeline definition

---

## 🎉 Summary

You now have **3 ways to run drift detection**:

| Command | Use Case | Time |
|---------|----------|------|
| `docker-compose run dvc-full-pipeline` | Complete ML + drift | 10-20 min |
| `docker-compose run dvc-drift-pipeline` | Drift monitoring | 2-5 min |
| `docker-compose run --profile drift-manual ...` | Debug/develop | 5-10 min |

**Recommendation**: Start with `dvc-full-pipeline` for complete runs, then use `dvc-drift-pipeline` for production monitoring.

---

**Status**: ✅ Ready to Use
**Version**: 3.1
**Last Updated**: 2025-11-17
