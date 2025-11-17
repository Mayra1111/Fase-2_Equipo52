# 🔀 Three DVC Pipeline Variants Guide

**Version**: 4.0
**Status**: ✅ Production Ready
**Date**: 2025-11-17

---

## Overview

Your project now supports **three independent DVC pipeline configurations**, each optimized for different purposes:

| Pipeline | Purpose | Time | When to Use |
|----------|---------|------|------------|
| **dvc_basic.yaml** | ML pipeline only | 10-15 min | Development, quick runs |
| **dvc_with_drift.yaml** | ML + drift detection | 15-20 min | Monitoring, quality assurance |
| **dvc_with_mlflow.yaml** | ML + experiment tracking | 10-15 min | Experimentation, tracking |

---

## 🚀 Quick Start (30 Seconds)

### Option 1: Basic Pipeline (No Drift)
```bash
# Run ML pipeline only
docker-compose run dvc-pipeline-basic

# Output: Model, metrics, visualizations
```

### Option 2: With Drift Detection
```bash
# Run ML pipeline + drift detection
docker-compose run dvc-pipeline-drift

# Output: Model, metrics, drift reports, visualizations
```

### Option 3: With MLflow Tracking
```bash
# Run ML pipeline with experiment tracking
docker-compose run dvc-pipeline-mlflow

# View results in MLflow UI
docker-compose up mlflow
# Access: http://localhost:5001
```

---

## 📊 Pipeline 1: BASIC (dvc_basic.yaml)

### Stages
```
┌─────────────────────────────────────────┐
│ Stage 1: EDA                            │
│ Exploratory Data Analysis               │
│ Input: obesity_estimation_modified.csv  │
│ Output: data/interim/*.csv              │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 2: Preprocess                     │
│ Feature Engineering & Scaling           │
│ Input: data/interim/*.csv               │
│ Output: Preprocessed features           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 3: Train                          │
│ Model Training (Multiple Algorithms)    │
│ Input: Preprocessed data                │
│ Output: models/best_pipeline.joblib     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 4: Evaluate                       │
│ Model Evaluation & Metrics              │
│ Input: Trained model                    │
│ Output: evaluation_metrics.json         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 5: Visualize                      │
│ EDA Visualizations & Reports            │
│ Input: Raw & processed data             │
│ Output: PNG plots in reports/figures/   │
└─────────────────────────────────────────┘
```

### Usage
```bash
# Run via Docker Compose (RECOMMENDED)
docker-compose run dvc-pipeline-basic

# Or run directly with DVC
dvc repro -f dvc_basic.yaml

# Or run a specific stage
dvc repro -f dvc_basic.yaml -s train
```

### Output Files
```
models/
├── best_pipeline.joblib        ← Trained model
└── model_metadata.joblib       ← Model metadata

reports/
├── metrics/
│   └── evaluation_metrics.json
└── figures/
    ├── 01_dataset_overview.png
    ├── 02_numeric_distributions.png
    └── 06_correlation_matrix.png
```

### Best For
- ✅ Quick model development
- ✅ Baseline runs without monitoring
- ✅ Testing pipeline quickly
- ✅ Minimal resources needed
- ✅ Production model training

---

## 🔍 Pipeline 2: WITH DRIFT (dvc_with_drift.yaml)

### Stages
```
[Previous 5 stages: EDA → Preprocess → Train → Evaluate → Visualize]
               ↓
┌─────────────────────────────────────────┐
│ Stage 6: Simulate Drift                 │
│ Create Synthetic Drifted Dataset        │
│ Shifts features by 0.5 std + 3% noise   │
│ Output: dataset_with_drift.csv          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 7: Detect Drift                   │
│ Compare Baseline vs Drifted Data        │
│ Metrics: PSI, KS-test, Mann-Whitney     │
│ Output: drift_report.json, alerts.txt   │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ Stage 8: Visualize Drift                │
│ Generate Drift Analysis Plots           │
│ Output: Drift visualizations            │
└─────────────────────────────────────────┘
```

### Usage
```bash
# Run via Docker Compose (RECOMMENDED)
docker-compose run dvc-pipeline-drift

# Or run directly with DVC
dvc repro -f dvc_with_drift.yaml

# Or resume from specific stage
dvc repro -f dvc_with_drift.yaml -s detect_drift
```

### Output Files (Includes all from Basic + Drift)
```
reports/
├── drift/
│   ├── drift_report.json           ← Detailed metrics
│   └── drift_alerts.txt            ← Alert summaries
└── figures/
    ├── 10_drift_distributions.png
    ├── 11_drift_performance_comparison.png
    └── 12_drift_psi_heatmap.png
```

### Drift Detection Metrics
- **PSI** (Population Stability Index) - Distribution changes
- **KS Test** (Kolmogorov-Smirnov) - Statistical comparison
- **Mann-Whitney U Test** - Non-parametric test
- **Threshold**: Drift detected if any metric exceeds threshold

### Best For
- ✅ Production monitoring
- ✅ Data quality assurance
- ✅ Detecting model performance degradation
- ✅ Regulatory compliance
- ✅ Scheduled monitoring jobs
- ✅ CI/CD drift validation

---

## 📈 Pipeline 3: WITH MLFLOW (dvc_with_mlflow.yaml)

### Stages
```
[Stages 1-5: Same as Basic Pipeline]

BUT: Stage 3 (Train) automatically logs to MLflow
     Stage 4 (Evaluate) logs metrics to MLflow

All experiments tracked in MLflow UI
```

### Features
- ✅ Experiment tracking
- ✅ Automatic metric logging
- ✅ Parameter versioning
- ✅ Model artifacts storage
- ✅ Run comparison
- ✅ Hyperparameter tuning tracking

### Usage
```bash
# Run pipeline with MLflow tracking
docker-compose run dvc-pipeline-mlflow

# Start MLflow UI in separate terminal
docker-compose up mlflow

# Access MLflow dashboard
# http://localhost:5001
```

### MLflow Integration
```yaml
# Automatically tracked by MLflow:
- Training parameters (algorithms, hyperparameters)
- Metrics (accuracy, precision, recall, F1-score)
- Model artifacts (joblib files)
- Training duration
- Model comparison across runs
```

### Output Files
```
Same as Basic Pipeline +

mlruns/
├── 0/                           ← Experiment directory
│   ├── meta.yaml               ← Experiment metadata
│   └── [run_id]/
│       ├── params/              ← Parameters logged
│       ├── metrics/             ← Metrics logged
│       └── artifacts/           ← Model artifacts
```

### Viewing Results
```bash
# Start MLflow UI
docker-compose up mlflow

# Or run standalone
mlflow ui --port 5001

# Browser: http://localhost:5001
```

### MLflow Dashboard Shows
- ✅ All experiment runs
- ✅ Parameter comparison
- ✅ Metric comparison
- ✅ Run duration
- ✅ Model artifacts
- ✅ Run notes/tags

### Best For
- ✅ Hyperparameter tuning
- ✅ Experiment comparison
- ✅ Model version management
- ✅ Team collaboration
- ✅ Research and development
- ✅ Model registry integration

---

## 🔄 Comparison Table

| Feature | Basic | Drift | MLflow |
|---------|-------|-------|--------|
| **EDA** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Preprocessing** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Model Training** | ✅ Yes | ✅ Yes | ✅ Yes (tracked) |
| **Model Evaluation** | ✅ Yes | ✅ Yes | ✅ Yes (tracked) |
| **Visualizations** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Drift Detection** | ❌ No | ✅ Yes | ❌ No |
| **MLflow Tracking** | ❌ No | ❌ No | ✅ Yes |
| **Time (approx)** | 10-15 min | 15-20 min | 10-15 min |
| **Resources** | Low | Medium | Low |
| **Best for Dev** | ✅ Yes | ⚠️ Partial | ✅ Yes |
| **Best for Prod** | ✅ Yes | ✅ Yes | ⚠️ Tracking |
| **Best for Monitoring** | ❌ No | ✅ Yes | ❌ No |
| **Best for Experiments** | ❌ No | ❌ No | ✅ Yes |

---

## 📋 When to Use Each Pipeline

### Use **dvc_basic.yaml** when:
- Building/testing the model
- Quick validation runs
- Minimal overhead needed
- Baseline performance establishment
- Production deployment (clean pipeline)
- Simple CI/CD workflows

### Use **dvc_with_drift.yaml** when:
- Monitoring production models
- Data quality assurance
- Drift detection compliance
- Regular scheduled checks
- Detecting performance degradation
- Quality gates in pipelines

### Use **dvc_with_mlflow.yaml** when:
- Tuning hyperparameters
- Comparing model variants
- Team collaboration on experiments
- Publishing model results
- Tracking experiment history
- Model registry management

---

## 🚀 Docker Compose Services

### New Services (Profile: dvc-pipelines)

```bash
# Basic pipeline
docker-compose run dvc-pipeline-basic

# Drift pipeline
docker-compose run dvc-pipeline-drift

# MLflow pipeline
docker-compose run dvc-pipeline-mlflow
```

### Legacy Services (Still Available)

```bash
# Basic (same as dvc-pipeline-basic)
docker-compose run dvc-pipeline

# Drift (same as dvc-pipeline-drift)
docker-compose run dvc-full-pipeline

# Drift-only
docker-compose run dvc-drift-pipeline
```

---

## 📊 Configuration

### Parameters (config/params.yaml)

All pipelines use the same parameters file:
```yaml
data:
  raw_path: data/raw
  interim_path: data/interim
  test_size: 0.2

preprocessing:
  create_bmi: true
  handle_outliers: true

models:
  algorithms:
    - RandomForest
    - GradientBoosting

mlflow:
  experiment_name: obesity_classification
```

### Environment Variables

```bash
# DVC Configuration
export DVC_REMOTE_URL=s3://bucket/path
export DVC_REMOTE_NAME=myremote

# MLflow Configuration (for dvc_with_mlflow.yaml)
export MLFLOW_TRACKING_URI=file:///app/mlruns
# or
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
```

---

## 🔧 Advanced Usage

### Run Specific Stage

```bash
# Run only the training stage
dvc repro -f dvc_basic.yaml -s train

# Run from training onwards
dvc repro -f dvc_basic.yaml -s train::

# Run multiple specific stages
dvc repro -f dvc_with_drift.yaml -s train -s detect_drift
```

### Force Rerun

```bash
# Rerun all stages (ignore cache)
dvc repro -f dvc_basic.yaml --force

# Rerun specific stage
dvc repro -f dvc_basic.yaml -s train --force
```

### Dry Run (View without executing)

```bash
# Show what would run without executing
dvc repro -f dvc_basic.yaml --dry
```

### Check Pipeline Status

```bash
docker-compose run shell dvc status -f dvc_basic.yaml
docker-compose run shell dvc dag -f dvc_with_drift.yaml
```

---

## 📚 Combined Usage Examples

### Example 1: Development Workflow

```bash
# 1. Quick development with basic pipeline
docker-compose run dvc-pipeline-basic

# 2. Review outputs in reports/
ls -la reports/

# 3. When satisfied, run with MLflow tracking
docker-compose run dvc-pipeline-mlflow

# 4. Compare experiments in MLflow
docker-compose up mlflow  # http://localhost:5001
```

### Example 2: Production Deployment

```bash
# 1. Final model training
docker-compose run dvc-pipeline-basic

# 2. Promote model to production
# (copy models/best_pipeline.joblib to prod)

# 3. Setup daily drift monitoring
# (cron job that runs dvc-pipeline-drift)
```

### Example 3: Quality Assurance

```bash
# 1. Train model
docker-compose run dvc-pipeline-basic

# 2. Run with drift detection
docker-compose run dvc-pipeline-drift

# 3. Check drift alerts
cat reports/drift/drift_alerts.txt

# 4. View drift visualizations
open reports/figures/10_*.png
```

### Example 4: Hyperparameter Tuning

```bash
# 1. Run with MLflow tracking multiple times
docker-compose run dvc-pipeline-mlflow  # Run 1
docker-compose run dvc-pipeline-mlflow  # Run 2
docker-compose run dvc-pipeline-mlflow  # Run 3

# 2. Compare all runs in MLflow
docker-compose up mlflow
# http://localhost:5001

# 3. Identify best configuration
# (view metrics and parameters in dashboard)

# 4. Deploy best model
```

---

## ✅ Verification Checklist

### After dvc_basic.yaml

- [ ] `models/best_pipeline.joblib` exists
- [ ] `reports/metrics/evaluation_metrics.json` exists
- [ ] EDA plots in `reports/figures/`
- [ ] No errors in container output

### After dvc_with_drift.yaml

- [ ] All basic outputs exist
- [ ] `reports/drift/drift_report.json` exists
- [ ] `reports/drift/drift_alerts.txt` readable
- [ ] Drift plots in `reports/figures/10_*.png`

### After dvc_with_mlflow.yaml

- [ ] All basic outputs exist
- [ ] `mlruns/` directory populated
- [ ] MLflow UI accessible at http://localhost:5001
- [ ] Experiment runs visible in dashboard

---

## 🆘 Troubleshooting

### Issue: "Stage X failed"

```bash
# Check which stage failed
docker-compose run shell dvc repro -f dvc_basic.yaml --verbose

# Check specific stage dependencies
docker-compose run shell dvc dag -f dvc_basic.yaml

# Run problematic stage directly
docker-compose run shell python scripts/run_ml.py
```

### Issue: "File not found" error

```bash
# Check pipeline stages
dvc dag -f dvc_basic.yaml

# Verify dependencies exist
docker-compose run shell ls -la data/interim/
docker-compose run shell ls -la models/
```

### Issue: MLflow not tracking

```bash
# Verify MLflow service running
docker-compose up mlflow &

# Check MLFLOW_TRACKING_URI
docker-compose run shell echo $MLFLOW_TRACKING_URI

# View backend store
ls -la mlruns/
```

---

## 📖 Related Documentation

- [HYBRID_DOCKER_GUIDE.md](HYBRID_DOCKER_GUIDE.md) - Docker reference
- [DVC_DRIFT_ORCHESTRATION.md](DVC_DRIFT_ORCHESTRATION.md) - Drift detection guide
- [dvc.yaml](dvc.yaml) - Default pipeline (combined version)
- [dvc_basic.yaml](dvc_basic.yaml) - Basic pipeline definition
- [dvc_with_drift.yaml](dvc_with_drift.yaml) - Drift pipeline definition
- [dvc_with_mlflow.yaml](dvc_with_mlflow.yaml) - MLflow pipeline definition

---

## 🎯 Summary

You now have **three independent DVC pipelines**:

| Use This | For This |
|----------|----------|
| `dvc-pipeline-basic` | Quick ML pipeline |
| `dvc-pipeline-drift` | Monitoring + quality assurance |
| `dvc-pipeline-mlflow` | Experiment tracking |

**All are automatic, reproducible, and production-ready.**

---

**Status**: ✅ Ready to Use
**Version**: 4.0
**Last Updated**: 2025-11-17
**Commit**: c7b6916
