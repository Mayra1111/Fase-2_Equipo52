# 🔍 Detailed Comparison: DVC, AWS S3, and API (`ali` vs `eze`)

Comprehensive analysis of differences in data versioning, cloud storage, and API implementation between branches.

---

## 📊 Executive Summary

| Aspect | `ali` | `eze` | Impact |
|--------|-------|-------|----|
| **DVC Stages** | 5 stages | 8 stages | `eze` adds drift monitoring |
| **API Location** | `/api/` (root) | `/src/api/` (structured) | `eze` improves organization |
| **API Size** | ~1,390 lines | ~529 lines | `eze` refactored for simplicity |
| **AWS S3** | Same config | Same config | No differences |
| **DVC Remote** | Same setup | Same setup | Both use S3 remote |
| **MLflow** | Basic | Enhanced | `eze` adds drift entry points |

---

## 🔄 DVC Pipeline Comparison

### `ali` Branch: 5 Stages

```yaml
stages:
  1. eda              → Cleans raw data → dataset_limpio_refactored.csv
  2. preprocess       → Feature engineering, scaling → preprocessed data
  3. train            → Model training → best_pipeline.joblib
  4. evaluate         → Model evaluation → evaluation_metrics.json
  5. visualize        → EDA visualizations → PNG figures
```

**Execution Flow:**
```
Raw Data → EDA → Preprocess → Train → Evaluate → Visualize
            ↓        ↓          ↓        ↓          ↓
         Clean   Features   Model    Metrics   Figures
```

### `eze` Branch: 8 Stages (EXPANDED)

```yaml
stages:
  1. eda              → [SAME] Cleans raw data
  2. preprocess       → [SAME] Feature engineering
  3. train            → [SAME] Model training
  4. evaluate         → [SAME] Model evaluation
  5. visualize        → [SAME] EDA visualizations
  6. simulate_drift   → [NEW] Creates dataset_with_drift.csv
  7. detect_drift     → [NEW] Generates drift reports
  8. visualize_drift  → [NEW] Drift analysis charts
```

**Execution Flow:**
```
Raw Data → EDA → Preprocess → Train → Evaluate → Visualize
            ↓        ↓          ↓        ↓          ↓
         Clean   Features   Model    Metrics   Figures
                                        ↓
                                  Dataset ──→ Simulate ──→ Detect ──→ Visualize
                                  Baseline    Drift      Drift      Drift
```

---

## 📝 DVC Stage Differences in Detail

### Stage 1-5: Core ML Pipeline (IDENTICAL)

All 5 original stages are **exactly the same** in both branches:
- **eda**: `python scripts/run_eda.py`
- **preprocess**: `python scripts/run_preprocess.py`
- **train**: `python scripts/run_ml.py`
- **evaluate**: `python scripts/run_evaluate.py`
- **visualize**: `python scripts/generate_visualizations.py`

**Dependencies, parameters, and outputs are identical.**

### Stage 6: Simulate Drift (NEW in `eze`)

```yaml
simulate_drift:
  cmd: python scripts/simulate_drift.py
  deps:
    - scripts/simulate_drift.py
    - ${data.interim_path}                    # ← Depends on EDA output
    - src/utils/config.py
    - src/utils/logger.py
  outs:
    - data/interim/dataset_with_drift.csv    # ← Creates drift simulation
  desc: "Simula data drift modificando distribuciones del dataset base"
```

**Purpose:** Creates synthetic dataset with intentional drift for testing detection system.

**Dependencies:**
- Depends on: Clean dataset from stage 1 (eda)
- Used by: stage 7 (detect_drift)

### Stage 7: Detect Drift (NEW in `eze`)

```yaml
detect_drift:
  cmd: python scripts/detect_drift.py
  deps:
    - scripts/detect_drift.py
    - ${data.interim_path}                    # ← Baseline dataset
    - data/interim/dataset_with_drift.csv     # ← Drifted dataset
    - ${models.output_dir}/best_pipeline.joblib      # ← Trained model
    - ${models.output_dir}/model_metadata.joblib     # ← Model metadata
    - src/monitoring/drift_detector.py        # ← Detection logic
    - src/models/data_preprocessor.py
  outs:
    - reports/drift/drift_report.json         # ← Technical report
    - reports/drift/drift_alerts.txt          # ← Human-readable alerts
  desc: "Detección de data drift comparando baseline con dataset driftado"
```

**Purpose:** Detects drift using statistical methods (PSI, KS test) and generates reports.

**Dependencies:**
- Depends on: stages 1 (baseline), 6 (drifted data), 3-4 (model)
- Used by: stage 8 (visualize_drift)

### Stage 8: Visualize Drift (NEW in `eze`)

```yaml
visualize_drift:
  cmd: python scripts/visualize_drift.py
  deps:
    - scripts/visualize_drift.py
    - ${data.interim_path}                    # ← Baseline
    - data/interim/dataset_with_drift.csv     # ← Drifted
    - reports/drift/drift_report.json         # ← Drift metrics
    - src/utils/config.py
  outs:
    - reports/figures/10_drift_distributions.png          # ← Feature changes
    - reports/figures/11_drift_performance_comparison.png # ← Model degradation
    - reports/figures/12_drift_psi_heatmap.png           # ← PSI by feature
  desc: "Generación de visualizaciones para análisis de data drift"
```

**Purpose:** Creates 3 PNG visualizations showing drift analysis.

**Dependencies:**
- Depends on: stage 7 (drift detection results)
- Final stage in pipeline

---

## 🌍 AWS S3 and DVC Remote Configuration

### Configuration Status

**Both `ali` and `eze` branches: IDENTICAL**

The AWS S3 and DVC remote setup is **exactly the same** in both branches:

```yaml
# .dvc/config (Same in both branches)
['remote "myremote"']
    url = s3://itesm-mna/obesity-ml/data

# Environment Variables (Same in both)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
DVC_REMOTE_URL
```

### DVC Remote Operations

Both branches support:
- ✅ **dvc pull** - Download versioned data/models from S3
- ✅ **dvc push** - Upload artifacts to S3
- ✅ **dvc status** - Check sync status with S3
- ✅ **dvc fetch** - Download without updating workspace

### Data Versioning Artifacts

**Same in both branches:**
```
.dvc/
├── config          ← S3 remote configuration
├── .gitignore      ← DVC tracking
└── *.lock          ← Generated dependency locks
```

### Pipeline with S3 Integration

Both branches execute pipelines that interact with S3:

```bash
# Stage execution flow
dvc pull                # Download data from S3
dvc repro              # Run pipeline stages
dvc push               # Upload outputs back to S3
```

**Key Point:** The drift detection stages (6-8) in `eze` also integrate with S3:
- Stage 7 reads model from `${models.output_dir}/` (S3-tracked)
- Stage 7 outputs drift reports to `reports/drift/` (optional S3 tracking)
- Stage 8 outputs visualizations to `reports/figures/` (optional S3 tracking)

---

## 🔌 API Implementation Comparison

### API Directory Structure

#### `ali` Branch: Root-Level API

```
/api/
├── __init__.py           (11 lines)
├── main.py               (170 lines)
├── config.py             (44 lines)
├── dependencies.py       (140 lines)
├── schemas.py            (179 lines)
├── routers/
│   ├── __init__.py
│   ├── health.py         (80 lines)
│   ├── model_info.py     (185 lines)
│   └── prediction.py     (230 lines)
└── README.md             (351 lines)

Total: ~1,390 lines
Location: Root level (less structured)
```

#### `eze` Branch: Source-Level API (Refactored)

```
/src/api/
├── __init__.py           (25 lines)
├── main.py               (366 lines)
└── schemas.py            (138 lines)

Total: ~529 lines
Location: /src (better structured)
Removed: Separate routers, dependencies, config files
Reason: Consolidation for simplicity and Docker optimization
```

**Delta:** -861 lines (62% reduction through refactoring)

---

## 📋 API Endpoint Comparison

### Endpoints Available

Both branches provide **identical endpoints**, but with different implementation approaches:

| Endpoint | `ali` | `eze` | Purpose |
|----------|-------|-------|---------|
| **POST /predict** | ✅ | ✅ | Single prediction |
| **POST /predict/batch** | ✅ | ✅ | Batch predictions |
| **GET /health** | ✅ | ✅ | Health check |
| **GET /model/info** | ✅ | ✅ | Model metadata |
| **GET /docs** | ✅ | ✅ | Swagger UI |
| **GET /redoc** | ✅ | ✅ | ReDoc documentation |

### API Structure Implementation

#### `ali`: Modular Router-Based Architecture

```python
# api/main.py (170 lines) - Lightweight, imports routers
from .routers import health, prediction, model_info

app.include_router(health.router, prefix="/", tags=["Health"])
app.include_router(model_info.router, prefix="/model", tags=["Model"])
app.include_router(prediction.router, prefix="", tags=["Predictions"])

# api/routers/prediction.py (230 lines) - Handles all predictions
# api/routers/health.py (80 lines) - Health checks
# api/routers/model_info.py (185 lines) - Model information
```

**Pros:** Highly modular, easy to extend individual routers

**Cons:** More files to maintain, additional imports

#### `eze`: Consolidated Architecture

```python
# src/api/main.py (366 lines) - All endpoints in one file
# Direct endpoint definitions, no routers
@app.post("/predict")
async def predict(features: ObesityFeatures) -> PredictionResponse:
    # Direct implementation

@app.post("/predict/batch")
async def predict_batch(request: PredictionBatchRequest) -> PredictionBatchResponse:
    # Direct implementation

@app.get("/health")
async def health_check() -> HealthCheck:
    # Direct implementation

@app.get("/model/info")
async def get_model_info() -> ModelInfo:
    # Direct implementation
```

**Pros:** Simpler for small projects, fewer files, faster startup

**Cons:** Less modular, harder to extend

---

## 🛠️ API Dependencies and Configuration

### `ali`: Separate Config Files

```python
# api/config.py (44 lines)
class Settings(BaseSettings):
    app_name: str
    app_version: str
    model_path: str
    # ... other settings

# api/dependencies.py (140 lines)
class ModelLoader:
    def load_model(self):
        # Model loading logic

def get_model_loader():
    # Dependency injection
```

### `eze`: Unified Configuration

```python
# src/api/main.py (366 lines) - Integrated config and dependencies
# Settings read from:
MODELS_DIR = Path(...)
API_VERSION = "1.0.0"

# Model loading integrated in main.py
loader = joblib.load(MODEL_PATH)
```

---

## 📊 API Code Size Comparison

### Breakdown by Component

#### `ali` Branch (1,390 lines total)

```
main.py              170 lines (12%)
routers/prediction   230 lines (17%)
routers/model_info   185 lines (13%)
routers/health        80 lines (6%)
schemas.py           179 lines (13%)
dependencies.py      140 lines (10%)
config.py             44 lines (3%)
__init__.py           11 lines (1%)
README.md            351 lines (25%)
─────────────────────────────
Total              1,390 lines
```

#### `eze` Branch (529 lines total)

```
main.py              366 lines (69%)
schemas.py           138 lines (26%)
__init__.py           25 lines (5%)
─────────────────────────────
Total                529 lines
```

**Key Differences:**
- No separate routers (consolidated into main)
- No separate config.py (config in main)
- No separate dependencies.py (logic in main)
- API documentation moved to markdown files
- Overall 62% more compact

---

## 🔌 API Schemas Comparison

### `ali`: Detailed Schemas

```python
# api/schemas.py (179 lines)
class ObesityFeatures(BaseModel):
    # Feature validation

class PredictionResponse(BaseModel):
    # Response format

class ErrorResponse(BaseModel):
    # Error handling

# Plus: HealthResponse, ModelInfoResponse, etc.
```

### `eze`: Simplified Schemas

```python
# src/api/schemas.py (138 lines)
class ObesityFeatures(BaseModel):
    # Feature validation

class PredictionResponse(BaseModel):
    # Response format

class HealthCheck(BaseModel):
    # Health status

# Same functionality, more concise
```

**Delta:** -41 lines (23% reduction)

---

## 🚀 API Serving Differences

### Execution

Both branches start the API the same way:

```bash
# Both branches
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Or in Docker
docker-compose up api
```

### Docker Integration

#### `ali`: Separate Dockerfile.api

```dockerfile
# Dockerfile.api (lightweight API-only)
FROM python:3.11-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `eze`: Single Dockerfile (No API-specific variant)

```dockerfile
# Dockerfile (unified)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Runs any command via docker-compose
```

**Change Reason:** `eze` uses unified Docker image for all services (reduces complexity)

---

## 📈 Docker Compose API Service

### `ali`: API Service Configuration

```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile.api          # ← Lightweight variant
  container_name: obesity-ml-api
  ports:
    - "8000:8000"                       # ← Exposes port
  volumes:
    - ./models:/app/models
    - ./api:/app/api
  command: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### `eze`: API Service (If Included)

```yaml
# NOTE: eze branch does NOT include API service in docker-compose.yml
# API can be started separately with:
# docker-compose run --rm ml-pipeline python -m uvicorn src.api.main:app

# Reason: Focus on drift detection services in docker-compose
# API can be deployed independently or added as needed
```

**Note:** `eze` doesn't automatically start API in docker-compose, but it's deployable separately.

---

## 🔄 MLflow Integration

### `ali`: Basic MLflow

```python
# api/main.py - Simple model loading
model = load_model()  # Basic loading
```

No MLflow entry points in this branch.

### `eze`: Enhanced MLflow with Entry Points

```yaml
# MLproject (NEW)
entry_points:
  eda:
    command: "python scripts/run_eda.py"
  ml:
    command: "python scripts/run_ml.py"
  simulate_drift:       # ← NEW
    command: "python scripts/simulate_drift.py"
  detect_drift:         # ← NEW
    command: "python scripts/detect_drift.py"
  visualize_drift:      # ← NEW
    command: "python scripts/visualize_drift.py"
```

**Benefits:**
- Can run: `mlflow run . -e simulate_drift`
- Tracks experiment parameters
- Better workflow orchestration

---

## 🔐 API Authentication and Security

### Both Branches: Current Security

Both `ali` and `eze` implement:
- ✅ CORS middleware
- ✅ Request validation (Pydantic)
- ✅ Error handling
- ❌ No API key authentication
- ❌ No JWT tokens
- ❌ No rate limiting

**Note:** Both branches have identical security posture at the API level.

---

## 📦 Requirements Comparison

### `ali`: requirements.txt

```
Core: pandas, numpy, scikit-learn, joblib
API: fastapi, uvicorn, pydantic
MLflow: mlflow
```

### `eze`: requirements.txt (UPDATED)

```
Core: pandas, numpy, scikit-learn, joblib
API: fastapi, uvicorn, pydantic
MLflow: mlflow
Drift Detection: scipy==1.11.0 (NEW)  ← For statistical tests
```

**Single Addition:** `scipy==1.11.0` for:
- Kolmogorov-Smirnov test
- Mann-Whitney U test
- Other statistical distributions

---

## 📊 Summary Table: DVC, AWS, API

| Aspect | `ali` | `eze` | Change |
|--------|-------|-------|--------|
| **DVC Stages** | 5 | 8 | +3 drift stages |
| **AWS S3 Config** | ✅ | ✅ | No change |
| **DVC Remote** | ✅ | ✅ | No change |
| **API Location** | `/api/` | `/src/api/` | Restructured |
| **API Size** | 1,390 lines | 529 lines | -62% (refactored) |
| **API Routers** | 3 routers | Consolidated | Simplified |
| **API Endpoints** | Same (6) | Same (6) | No change |
| **Docker API** | Dockerfile.api | Dockerfile | Unified |
| **MLflow Entries** | None | 7 | +Drift entry points |
| **Requirements** | Standard | +scipy | +1 dependency |
| **Security** | CORS only | CORS only | No change |

---

## 🎯 Key Takeaways

### DVC Pipeline
- **Original 5 stages preserved exactly** in both branches
- **`eze` adds 3 new drift detection stages** (6, 7, 8)
- Pipeline dependency graph expanded but original flow unchanged

### AWS S3 Integration
- **No differences** between branches
- Both use same S3 remote configuration
- Both support dvc pull/push for data versioning
- Drift detection stages also respect S3 tracking

### API Implementation
- **All endpoints identical** between branches
- **`eze` refactored for simplicity**: 62% smaller code
- **`eze` consolidated routers**: fewer files, easier deployment
- **Same functionality, cleaner structure** in `eze`
- Security posture unchanged (both need enhancement for production)

### Recommendation

| Use Case | Branch | Reason |
|----------|--------|--------|
| **API-only serving** | Either | Endpoints identical |
| **Data versioning** | Either | S3 config identical |
| **Production deployment** | `eze` | Cleaner API code + drift monitoring |
| **API customization** | `ali` | More modular router structure |
| **Full MLOps pipeline** | `eze` | Drift detection + full orchestration |

---

## 🔗 Additional Resources

- **DVC Pipeline Details:** `dvc.yaml`
- **API Code:** `src/api/main.py`, `src/api/schemas.py`
- **Drift Detection:** `src/monitoring/drift_detector.py`, `scripts/detect_drift.py`
- **Full Branch Comparison:** `BRANCH_COMPARISON_ALI_VS_EZE.md`
- **DVC Integration Guide:** `DRIFT_DETECTION_GUIDE.md`

---

**Version:** 1.0.0
**Status:** ✅ Complete
**Last Updated:** 2025-11-17
**Branch:** eze
**Created for:** Technical Architecture Decision Making
