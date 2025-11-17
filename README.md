# Obesity Classification - Complete MLOps Pipeline (Fase 3)

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![DVC](https://img.shields.io/badge/DVC-3.55-orange.svg)](https://dvc.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![MLflow](https://img.shields.io/badge/MLflow-2.8-blue.svg)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green.svg)](https://fastapi.tiangolo.com/)
[![pytest](https://img.shields.io/badge/pytest-automated-red.svg)](https://pytest.org/)

**Equipo 52** - Complete MLOps project for obesity classification, featuring automated pipelines, data versioning, experiment tracking, FastAPI serving, and drift detection.

**Fase 3 - Complete Integration**: Automated testing, REST API, Reproducibility, Containerization, and Production Monitoring

---

## 📋 Quick Navigation

- **[⚡ 5-Minute Quickstart](#-5-minute-quickstart)** - Get running immediately
- **[✅ Fase 3 Objectives](#-fase-3-objectives-completed)** - What's implemented
- **[📊 Architecture](#-system-architecture)** - How it all works together
- **[🚀 Full Documentation](#-full-documentation)** - Deep dives into each component

---

## ⚡ 5-Minute Quickstart

```bash
# 1. Clone and setup
git clone <repo-url> && cd Fase-2_Equipo52
echo "AWS_ACCESS_KEY_ID=your_key" > .env
echo "AWS_SECRET_ACCESS_KEY=your_secret" >> .env

# 2. Build Docker image (3-5 min, first time only)
docker-compose build

# 3. Run ML pipeline (10-20 min)
docker-compose run --rm dvc-pipeline-basic
# OR: docker-compose run dvc-pipeline

# 4. Start API
docker-compose up -d api

# 5. Test the model
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 24, "height": 1.75, "weight": 85, "gender": "Male", ...}'

# 6. View results
# API Docs: http://localhost:8000/docs
# MLflow: http://localhost:5001
```

---

## ✅ Fase 3: Objectives Completed

### 1️⃣ Unit & Integration Testing

**Status**: ✅ **IMPLEMENTED**

- **Framework**: `pytest` with `conftest.py` fixtures
- **Coverage**: >80% of `src/` code
- **Types**: Unit tests, Integration tests, API endpoint tests
- **Execution**: Single command - `pytest tests/ -v --cov=src`
- **In Docker**: `docker-compose run --rm test`

**Key Test Suites**:
- `test_data_cleaner.py` - Data preprocessing validation
- `test_model_trainer.py` - Model training & validation
- `test_api.py` - FastAPI endpoint testing
- `test_integration_pipeline.py` - End-to-end pipeline tests

**Example Test**:
```python
def test_predict_endpoint(client):
    """Test POST /predict returns valid prediction"""
    response = client.post("/predict", json={...})
    assert response.status_code == 200
    assert "prediction" in response.json()
```

---

### 2️⃣ FastAPI Serving & Model Portability

**Status**: ✅ **IMPLEMENTED**

- **Framework**: FastAPI with Pydantic validation
- **Main Endpoint**: `POST /predict` - Individual predictions
- **Documentation**: Auto-generated Swagger UI at `/docs`
- **Model Version**: `v1.0.0` stored in `models/best_pipeline.joblib`
- **Validation**: Automatic input validation with error handling

**API Quick Reference**:

```bash
# Health check
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 24,
    "height": 1.75,
    "weight": 85,
    "gender": "Male",
    "FCVC": 2.0,
    "NCP": 3,
    "CH2O": 2.0,
    "FAF": 0.0,
    "TUE": 0,
    "SMOKE": false,
    "SCC": false,
    "MTRANS": "Public_Transportation"
  }'

# Model info
curl http://localhost:8000/model-info
```

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

**Model Artifact**:
- Path: `models/best_pipeline.joblib`
- Version: v1.0.0
- Metrics: Accuracy 92.34%, Precision 91.56%, Recall 91.98%, F1 91.77%

---

### 3️⃣ Reproducibility Verification

**Status**: ✅ **VERIFIED**

- **Fixed Dependencies**: All versions pinned in `requirements.txt`
- **Fixed Seeds**: Random state = 42 across all ML libraries
- **DVC Versioning**: Data and models tracked with `dvc.lock`
- **Reproducible Across Environments**: Same metrics in Docker on any machine

**Verification Steps**:
```bash
# Run pipeline
docker-compose run --rm dvc-pipeline-basic

# Compare metrics (should be identical to baseline)
diff baseline_metrics.json reports/metrics/evaluation_metrics.json
# Should have NO differences (or very minor floating-point differences)
```

**Metrics Reproducibility**:
| Metric | Baseline | Re-run | Status |
|--------|----------|--------|--------|
| Accuracy | 92.34% | 92.34% | ✅ Exact |
| Precision | 91.56% | 91.56% | ✅ Exact |
| Recall | 91.98% | 91.98% | ✅ Exact |
| F1-Score | 91.77% | 91.77% | ✅ Exact |

---

### 4️⃣ Docker Containerization

**Status**: ✅ **IMPLEMENTED**

- **Dockerfile**: Optimized multi-layer build
- **Base Image**: `python:3.10-slim` (~250MB)
- **Dependencies**: AWS CLI, DVC, all Python packages pre-installed
- **Build Command**: `docker build -t ml-service:latest .`
- **Run Command**: `docker run -p 8000:8000 ml-service:latest`
- **Registry**: Ready for DockerHub push

**Docker Commands**:
```bash
# Build image
docker build -t ml-service:v1.0.0 .

# Run container
docker run -p 8000:8000 ml-service:v1.0.0

# With Docker Compose
docker-compose up -d api

# Push to DockerHub
docker tag ml-service:v1.0.0 <username>/ml-service:v1.0.0
docker push <username>/ml-service:v1.0.0
```

---

### 5️⃣ Data Drift Detection

**Status**: ✅ **FULLY IMPLEMENTED**

- **Detection Methods**: PSI, Kolmogorov-Smirnov, Mann-Whitney U
- **Performance Monitoring**: Tracks accuracy degradation
- **Synthetic Data Generation**: Creates realistic drift scenarios
- **Automated Alerts**: Configured thresholds with recommendations
- **Visualizations**: 3 drift analysis charts generated

**Run Drift Detection** (included in main pipeline):
```bash
docker-compose run --rm dvc-pipeline-basic
# Pipeline includes drift detection stages:
# - simulate_drift: Creates synthetic drift scenarios
# - detect_drift: Analyzes drift with statistical tests
# - visualize_drift: Generates 3 drift analysis charts
# Outputs:
# - reports/drift/drift_report.json (quantitative results)
# - reports/drift/drift_alerts.txt (human-readable alerts)
# - 3 visualization PNG files in reports/figures/
```

**Alert Example**:
```
⚠️ DRIFT DETECTED - SEVERITY: MODERATE

Features with drift: age, weight, FCVC
Performance degradation: -3.27%
Recommended action: Schedule immediate retraining
```

**Thresholds**:
- PSI > 0.1: Moderate drift
- Performance loss > 3%: Warning
- Performance loss > 5%: Critical alert

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   USER INTERACTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  docker-run.sh (bash)    ┌─────────────────────────────────┐   │
│  docker-run.ps1 (ps)  ─→ │  FastAPI REST API              │   │
│  curl / Postman           │  http://localhost:8000/predict │   │
│                           └─────────────────────────────────┘   │
│                                                                 │
│                        ┌──────────────────┐                    │
│                        │  MLflow UI       │                    │
│                        │  localhost:5001  │                    │
│                        └──────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│             DOCKER COMPOSE ORCHESTRATION LAYER                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │  API Service   │  │  MLflow Server │  │  Test Runner     │ │
│  │  (FastAPI)     │  │  (Port 5001)   │  │  (pytest)        │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DVC Pipeline Services (choose one):                     │  │
│  │  • dvc-pipeline-basic (5 stages, 10-15 min)             │  │
│  │  • dvc-pipeline-drift (9 stages, 15-20 min)             │  │
│  │  • dvc-pipeline-mlflow (6 stages, 10-15 min)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              DATA PIPELINE EXECUTION LAYER (DVC)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EDA → Preprocess → Train → Evaluate → Visualize → Test       │
│                                                                 │
│  (With drift detection: + Simulate Drift → Detect Drift       │
│                          → Visualize Drift)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE & ARTIFACTS LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DVC Cache        Models            Data          Reports      │
│  ├─ .dvc/         ├─ best_pipeline  ├─ raw/       ├─ metrics   │
│  └─ dvc.lock      ├─ model_metadata ├─ interim/   ├─ figures   │
│                   └─ (v1.0.0)       └─ processed/ └─ drift/    │
│                                                                 │
│  Git Repository   S3/Azure/GCS Remote Storage                  │
│  (Code versioning) (Data & Model versioning)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Full Documentation

### Getting Started

1. **[Setup & Configuration](#setup--configuration)**
2. **[Running Pipelines](#running-pipelines)**
3. **[Testing](#testing)**
4. **[API Usage](#api-usage)**
5. **[Monitoring & Drift Detection](#monitoring--drift-detection)**

### Setup & Configuration

```bash
# 1. Environment variables
cp config/docker.env.template .env
# Edit .env with your AWS credentials (or use local S3 mock)

# 2. Build Docker image
docker-compose build

# 3. Verify setup
docker-compose run --rm shell dvc status
```

### Running Pipelines

**Single Unified Pipeline** (includes all functionality):

```bash
docker-compose run --rm dvc-pipeline-basic
# OR: docker-compose run dvc-pipeline

# Runs (9 stages total):
#  1. EDA - Exploratory Data Analysis
#  2. Preprocess - Feature engineering, scaling
#  3. Train - Model training with cross-validation
#  4. Evaluate - Model evaluation and metrics
#  5. Visualize - Report and chart generation
#  6. simulate_drift - Create synthetic drift scenarios
#  7. detect_drift - Detect data drift with statistical tests
#  8. visualize_drift - Generate drift analysis visualizations
#  9. test - Run unit tests with coverage
#
# Duration: 15-20 minutes
# All stages run automatically in sequence
# Includes: Data versioning, reproducibility, drift detection, and testing
```

### Testing

```bash
# All tests with coverage report
pytest tests/ -v --tb=short --cov=src --cov-report=html

# Quick test (summary only)
pytest tests/ -q

# Specific test file
pytest tests/test_api.py -v

# In Docker
docker-compose run --rm test
```

### API Usage

**Start the API**:
```bash
docker-compose up -d api
```

**Make predictions**:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 24,
    "height": 1.75,
    "weight": 85,
    "gender": "Male",
    "FCVC": 2.0,
    "NCP": 3,
    "CH2O": 2.0,
    "FAF": 0.0,
    "TUE": 0,
    "SMOKE": false,
    "SCC": false,
    "MTRANS": "Public_Transportation"
  }'
```

**Response**:
```json
{
  "prediction": "Overweight_Level_II",
  "confidence": 0.95,
  "model_version": "v1.0.0",
  "timestamp": "2025-11-17T16:30:45.123Z"
}
```

**View API documentation**:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Monitoring & Drift Detection

```bash
# Check current model performance
curl http://localhost:8000/model-info

# Run full pipeline including drift detection
docker-compose run --rm dvc-pipeline-basic

# View drift report
cat reports/drift/drift_alerts.txt

# View drift visualizations (generated automatically)
open reports/figures/10_drift_distributions.png
open reports/figures/11_drift_performance_comparison.png
open reports/figures/12_drift_psi_heatmap.png
```

---

## 📁 Project Structure

```
Fase-2_Equipo52/
├── 📖 DOCUMENTATION & SETUP
│   ├── README.md                         ← You are here
│   ├── DVC_PIPELINES_SETUP.md            ← DVC detailed guide
│   ├── QUICK_START_HYBRID.md             ← Step-by-step setup
│   ├── config/params.yaml                ← Pipeline parameters
│   └── .env                              ← Credentials (local only)
│
├── 🔄 DVC PIPELINES (Choose ONE)
│   ├── dvc_basic.yaml                    ← Pipeline 1: Basic ML (5 stages)
│   ├── dvc_with_drift.yaml               ← Pipeline 2: + Drift (9 stages)
│   ├── dvc_with_mlflow.yaml              ← Pipeline 3: + MLflow (6 stages)
│   ├── dvc.lock                          ← Auto-generated dependency graph
│   └── scripts/run_dvc_pipeline.sh       ← Wrapper script
│
├── 🐳 DOCKER & DEPLOYMENT
│   ├── Dockerfile                        ← Image definition
│   ├── docker-compose.yml                ← Service orchestration
│   ├── docker-run.sh                     ← Bash helper script
│   ├── docker-run.ps1                    ← PowerShell helper
│   └── requirements.txt                  ← Python dependencies (pinned)
│
├── 🤖 MODEL & API (src/)
│   ├── api/
│   │   ├── main.py                       ← 🔴 FastAPI application
│   │   ├── schemas.py                    ← Pydantic validation
│   │   └── dependencies.py               ← Dependency injection
│   ├── data/
│   │   ├── data_loader.py
│   │   ├── data_cleaner.py               ← 🔴 Data preprocessing
│   │   └── data_preprocessor.py
│   ├── models/
│   │   ├── model_trainer.py              ← Model training
│   │   ├── model_evaluator.py            ← Evaluation metrics
│   │   └── drift_detector.py             ← Drift detection
│   └── visualization/
│       ├── eda_visualizer.py
│       └── drift_visualizer.py
│
├── 📊 DATA PIPELINE (scripts/)
│   ├── run_eda.py                        ← Stage 1: EDA
│   ├── run_preprocess.py                 ← Stage 2: Preprocessing
│   ├── run_ml.py                         ← Stage 3: Training
│   ├── run_evaluate.py                   ← Stage 4: Evaluation
│   ├── generate_visualizations.py        ← Stage 5: Visualize
│   ├── simulate_drift.py                 ← Stage 6 (drift): Simulate
│   ├── detect_drift.py                   ← Stage 7 (drift): Detect
│   └── visualize_drift.py                ← Stage 8 (drift): Visualize
│
├── 🧪 TESTS
│   ├── test_data_cleaner.py              ← Unit tests: data
│   ├── test_model_trainer.py             ← Unit tests: training
│   ├── test_api.py                       ← Integration: API endpoints
│   ├── test_integration_pipeline.py      ← E2E: full pipeline
│   └── conftest.py                       ← pytest fixtures
│
├── 📦 OUTPUTS & ARTIFACTS
│   ├── data/
│   │   ├── raw/                          ← Original data
│   │   ├── interim/                      ← Processed data
│   │   └── processed/                    ← Final data
│   ├── models/
│   │   ├── best_pipeline.joblib          ← 🔴 Trained model (v1.0.0)
│   │   └── model_metadata.joblib         ← Model metadata
│   ├── reports/
│   │   ├── metrics/evaluation_metrics.json  ← Performance metrics
│   │   ├── figures/                      ← Visualization PNGs
│   │   └── drift/                        ← Drift reports & alerts
│   └── mlruns/                           ← MLflow experiments
│
└── 🔧 VERSION CONTROL
    ├── .git/                             ← Git repository
    ├── .gitignore                        ← Excluded files
    └── .dvc/                             ← DVC metadata
```

---

## 🧪 Testing Strategy

### Test Coverage

| Component | Type | Coverage | Location |
|-----------|------|----------|----------|
| **Data Cleaning** | Unit | 85% | `test_data_cleaner.py` |
| **Model Training** | Unit | 80% | `test_model_trainer.py` |
| **Evaluation** | Unit | 90% | `test_model_evaluator.py` |
| **API Endpoints** | Integration | 100% | `test_api.py` |
| **Full Pipeline** | E2E | N/A | `test_integration_pipeline.py` |

### Running Tests

```bash
# Full test suite with coverage
pytest tests/ -v --tb=short --cov=src --cov-report=html

# Quick test run
pytest tests/ -q

# Single test
pytest tests/test_api.py::test_predict_endpoint -v

# In Docker
docker-compose run --rm test
```

---

## 📈 Model Performance

**Current Model**: XGBoost classifier (v1.0.0)
**Training Data**: 2,153 samples
**Target Classes**: 7 obesity levels

| Metric | Value |
|--------|-------|
| **Accuracy** | 92.34% |
| **Precision** | 91.56% |
| **Recall** | 91.98% |
| **F1-Score** | 91.77% |
| **Training Time** | ~5 minutes |

---

## 🔧 Common Commands

### Pipeline Management
```bash
docker-compose run --rm dvc-pipeline-basic    # Run full pipeline
docker-compose run dvc-pipeline               # Alternative

dvc status                                    # Check pipeline status
dvc dag                                       # View pipeline DAG
dvc metrics show                              # Display metrics
dvc repro                                     # Reproduce pipeline locally
```

### Testing
```bash
pytest tests/ -v --cov=src      # Full test suite
docker-compose run --rm test    # Tests in Docker
```

### API & Services
```bash
docker-compose up -d api        # Start API
docker-compose up -d mlflow     # Start MLflow
docker-compose logs -f api      # View logs
```

### Data Management
```bash
dvc pull                         # Download data/models
dvc push                         # Upload data/models
dvc add data/interim/*.csv      # Version new files
```

### Cleanup
```bash
docker-compose down              # Stop services (keep volumes)
docker-compose down -v           # Stop and remove volumes
docker system prune -a           # Clean unused Docker resources
```

---

## 🐛 Troubleshooting

### Pipeline Issues

**Problem**: "Stage not found"
```bash
# Solution:
chmod +x scripts/run_dvc_pipeline.sh
dvc status && dvc dag
git checkout dvc.yaml
```

**Problem**: API not responding
```bash
# Solution:
docker-compose logs api
docker-compose restart api
curl http://localhost:8000/health
```

**Problem**: Tests failing
```bash
# Solution:
pytest tests/ -vv --tb=long  # More detailed output
pytest tests/ -s             # Show print statements
```

### Docker Issues

**Problem**: Image build fails
```bash
# Solution:
docker-compose build --no-cache
docker system prune -a
```

**Problem**: Permissions errors
```bash
# Solution:
docker-compose run --rm shell chmod -R 755 data/
```

---

## 📚 Additional Documentation

For detailed information, see:

- **[DVC_PIPELINES_SETUP.md](DVC_PIPELINES_SETUP.md)** - DVC pipeline configuration
- **[QUICK_START_HYBRID.md](QUICK_START_HYBRID.md)** - Step-by-step setup guide
- **[config/params.yaml](config/params.yaml)** - Pipeline parameters
- **[Dockerfile](Dockerfile)** - Docker image configuration
- **[docker-compose.yml](docker-compose.yml)** - Service definitions

---

## 🎓 MLOps Best Practices Implemented

✅ **Data Versioning**: DVC tracks all data artifacts
✅ **Model Versioning**: Trained models stored with metadata
✅ **Experiment Tracking**: MLflow logs all experiments
✅ **Automated Testing**: pytest with >80% coverage
✅ **Reproducibility**: Fixed seeds and pinned dependencies
✅ **Container Orchestration**: Docker Compose manages services
✅ **API Serving**: FastAPI with Pydantic validation
✅ **Production Monitoring**: Drift detection and alerts
✅ **Documentation**: Comprehensive README and guides
✅ **CI/CD Ready**: Scripts for automated deployment

---

## 🤝 Support

**Issues or Questions?**

1. Check existing documentation (links above)
2. Review test files for usage examples
3. Check `docker-compose logs` for error details
4. Run `dvc status` and `dvc dag` for pipeline info

**Equipo 52 - MLOps Project**
- 📧 Contact: equipo52@itesm.mx
- 🔗 Repository: [GitHub Link]
- 📊 Tracking: MLflow at http://localhost:5001

---

## 📋 Fase 3 Completion Checklist

- [x] Pruebas Unitarias e Integración (pytest >80% coverage)
- [x] Serving y Portabilidad (FastAPI, Docker, reproducibility)
- [x] Reproducibilidad Verificada (fixed seeds, pinned deps)
- [x] Containerización (Dockerfile, docker-compose, DockerHub)
- [x] Data Drift Detection (PSI, KS, Mann-Whitney, alerts)
- [x] Documentación Completa (this README + guides)
- [x] Ready for Production

---

**Last Updated**: 2025-11-17
**Project Version**: v3.0-hybrid
**Status**: ✅ Fase 3 Complete - Production Ready

