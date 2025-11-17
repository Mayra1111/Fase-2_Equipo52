# DVC Multiple Pipeline Files Setup

## Overview

This project uses **three separate DVC pipeline files** instead of a single `dvc.yaml`. This approach provides clarity, maintainability, and flexibility for different use cases.

## Why Three Separate Files?

### ✅ Benefits of Multiple Files

1. **Clarity**: Each pipeline's purpose is explicit and self-contained
2. **No Complex Conditionals**: Avoids conditional logic in DVC (which isn't well-supported)
3. **Easy to Extend**: Modify one pipeline without affecting others
4. **Team-Friendly**: Clear separation of concerns for collaboration
5. **Docker-Friendly**: Perfect for docker-compose service organization

### ❌ Problems with Single File Approach

- DVC doesn't support native conditional stages
- Complex parameter-driven workarounds are error-prone
- Harder to understand and maintain
- All stages appear in `dvc dag` even if not used

## Pipeline Files

### 1. **dvc_basic.yaml** - Basic ML Pipeline (5 stages)
```
EDA → Preprocess → Train → Evaluate → Visualize → Test
```
**Use Case**: Development, quick iterations, basic ML workflow

**Command**:
```bash
./docker-run.sh dvc-basic
docker-compose run dvc-pipeline-basic
```

### 2. **dvc_with_drift.yaml** - ML + Drift Detection (9 stages)
```
EDA → Preprocess → Train → Evaluate → Visualize
→ Simulate Drift → Detect Drift → Visualize Drift → Test
```
**Use Case**: Production monitoring, detecting data quality issues

**Command**:
```bash
./docker-run.sh dvc-drift
docker-compose run dvc-pipeline-drift
```

### 3. **dvc_with_mlflow.yaml** - ML + Experiment Tracking (6 stages)
```
EDA → Preprocess → Train [logged] → Evaluate [logged] → Visualize → Test
```
**Use Case**: Experiment tracking, hyperparameter tuning, model comparison

**Command**:
```bash
./docker-run.sh dvc-mlflow
docker-compose run dvc-pipeline-mlflow
```

## How It Works

### The Wrapper Script

A helper script (`scripts/run_dvc_pipeline.sh`) manages the multiple files:

```bash
#!/bin/bash
# Temporarily swaps pipeline files before running DVC
1. Backs up existing dvc.yaml
2. Copies chosen pipeline file to dvc.yaml
3. Runs: dvc repro
4. Restores original dvc.yaml
```

This approach ensures:
- DVC works with its standard expected `dvc.yaml` file
- Original pipeline file is always preserved
- Clean process with automatic cleanup

### Docker Integration

Each docker-compose service uses the wrapper script:

```yaml
dvc-pipeline-basic:
  command: bash scripts/run_dvc_pipeline.sh dvc_basic.yaml

dvc-pipeline-drift:
  command: bash scripts/run_dvc_pipeline.sh dvc_with_drift.yaml

dvc-pipeline-mlflow:
  command: bash scripts/run_dvc_pipeline.sh dvc_with_mlflow.yaml
```

## Usage

### Via Docker Compose (Recommended)

```bash
# Run basic ML pipeline
docker-compose run dvc-pipeline-basic

# Run with drift detection
docker-compose run dvc-pipeline-drift

# Run with MLflow tracking
docker-compose run dvc-pipeline-mlflow
```

### Via Helper Scripts

**Linux/Mac (Bash)**:
```bash
./docker-run.sh dvc-basic
./docker-run.sh dvc-drift
./docker-run.sh dvc-mlflow
```

**Windows (PowerShell)**:
```powershell
.\docker-run.ps1 dvc-basic
.\docker-run.ps1 dvc-drift
.\docker-run.ps1 dvc-mlflow
```

### Direct DVC Commands (Inside Container)

```bash
bash scripts/run_dvc_pipeline.sh dvc_basic.yaml
bash scripts/run_dvc_pipeline.sh dvc_with_drift.yaml
bash scripts/run_dvc_pipeline.sh dvc_with_mlflow.yaml
```

## Main dvc.yaml File

A main `dvc.yaml` file is preserved as a reference/template. It contains the complete ML pipeline without drift detection.

**Note**: When running alternative pipelines, the wrapper script temporarily replaces this file but always restores it afterward.

## File Preservation

The wrapper script includes safety mechanisms:

```bash
# Before running pipeline
if [ -f "dvc.yaml" ]; then
    cp dvc.yaml dvc.yaml.bak  # Backup
fi

# Run pipeline
dvc repro

# After pipeline (regardless of success/failure)
if [ -f "dvc.yaml.bak" ]; then
    mv dvc.yaml.bak dvc.yaml  # Restore
fi
```

## Stage Details

### All Pipelines Include

Each pipeline includes these common stages:

1. **EDA** (run_eda.py)
   - Data loading and cleaning
   - Exploratory analysis
   - Output: `data/interim/dataset_limpio_refactored.csv`

2. **Preprocess** (run_preprocess.py)
   - Feature engineering
   - Data scaling
   - BMI calculation

3. **Train** (run_ml.py)
   - Model training
   - Cross-validation
   - (MLflow variant: automatic experiment logging)

4. **Evaluate** (run_evaluate.py)
   - Model evaluation
   - Metric calculation
   - (MLflow variant: metric logging)

5. **Visualize** (generate_visualizations.py)
   - EDA visualizations
   - Performance plots
   - Correlation matrices

6. **Test** (pytest)
   - Unit tests
   - Code coverage
   - Validation tests

### Drift Pipeline Only

7. **Simulate Drift** (simulate_drift.py)
   - Generate synthetic drifted data
   - Realistic drift scenarios

8. **Detect Drift** (detect_drift.py)
   - Compare baseline vs drifted data
   - Generate drift alerts

9. **Visualize Drift** (visualize_drift.py)
   - Drift analysis plots
   - PSI heatmaps
   - Performance comparison

## Dependencies and Outputs

### Data Flow

```
data/raw/obesity_estimation_modified.csv
    ↓
[EDA] → data/interim/dataset_limpio_refactored.csv
    ↓
[Preprocess] → processed features
    ↓
[Train] → models/best_pipeline.joblib
    ↓
[Evaluate] → reports/metrics/evaluation_metrics.json
    ↓
[Visualize] → reports/figures/*.png
    ↓
[Test] → test results
    ↓
[Simulate Drift] → data/interim/dataset_with_drift.csv
    ↓
[Detect Drift] → reports/drift/drift_report.json
    ↓
[Visualize Drift] → reports/figures/10_drift_*.png
```

## DVC Lock File

DVC creates a `dvc.lock` file to track stage dependencies and outputs:

```bash
# View pipeline DAG
dvc dag

# Check pipeline status
dvc status

# Repro specific stages
dvc repro --single-item train
```

## Troubleshooting

### Pipeline Not Running

```bash
# Check if wrapper script is executable
ls -la scripts/run_dvc_pipeline.sh
# Should show: -rwxr-xr-x (executable)

# Make executable if needed
chmod +x scripts/run_dvc_pipeline.sh

# Test manually
bash scripts/run_dvc_pipeline.sh dvc_basic.yaml
```

### DVC Remote Issues

```bash
# Configure S3 remote
dvc remote add -d remote-equipo52 s3://your-bucket/path
dvc remote modify remote-equipo52 profile your_aws_profile

# Push data
dvc push

# Pull data
dvc pull
```

### File Restoration Issues

If `dvc.yaml` isn't restored properly:

```bash
# Manually restore from backup
cp dvc.yaml.bak dvc.yaml

# Or restore from git
git checkout dvc.yaml
```

## Parameters

All pipelines use parameters from `config/params.yaml`:

```yaml
data:
  raw_path: "data/raw/obesity_estimation_modified.csv"
  interim_path: "data/interim/dataset_limpio_refactored.csv"
  test_size: 0.2
  random_state: 42

preprocessing:
  create_bmi: true
  handle_outliers: true
  scale_features: true

models:
  algorithms:
    - random_forest
    - xgboost
    - svm
  output_dir: "models"

training:
  cross_validation: true
  cv_folds: 5
  scoring: "f1_weighted"

evaluation:
  metrics:
    - accuracy
    - precision
    - recall
    - f1
  generate_plots: true

mlflow:
  experiment_name: "obesity-classification"
```

## Best Practices

1. **Always use the wrapper script or helper commands**
   - Don't run `dvc repro` directly
   - Don't manually swap pipeline files

2. **Check status before running**
   ```bash
   dvc status
   ```

3. **Use profiles in docker-compose**
   ```bash
   # Only run DVC pipelines
   docker-compose --profile dvc-pipelines run dvc-pipeline-basic
   ```

4. **Track DVC files in git**
   ```bash
   git add dvc*.yaml dvc.lock .dvc/config
   ```

5. **Don't commit sensitive data**
   - Use `.env` for credentials
   - Keep `data/` and `models/` in `.gitignore`

## Comparison Table

| Feature | Basic | Drift | MLflow |
|---------|-------|-------|--------|
| Stages | 6 | 9 | 6 |
| Duration | 10-15 min | 15-20 min | 10-15 min |
| Use Case | Development | Monitoring | Experimentation |
| Drift Detection | ❌ | ✅ | ❌ |
| Experiment Tracking | ❌ | ❌ | ✅ |
| Recommended | Quick dev | Production | Research |

## Additional Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC Pipelines Guide](https://dvc.org/doc/user-guide/pipelines)
- [MLflow Documentation](https://mlflow.org/docs)
- [Drift Detection README](README_DRIFT_DETECTION.md)
- [THREE_DVC_PIPELINES.md](THREE_DVC_PIPELINES.md)

## Questions?

For issues or questions about the pipeline setup:

1. Check `scripts/run_dvc_pipeline.sh` for the implementation
2. Review individual `dvc_*.yaml` files for stage details
3. Check `docker-compose.yml` for service configuration
4. See `config/params.yaml` for parameter definitions

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Status**: Production Ready
