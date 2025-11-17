# 🔀 Comparación de Ramas: `ali` vs `ivan/features`

## 📊 Resumen Ejecutivo

| Aspecto | Rama `ali` | Rama `ivan/features` | Diferencia |
|---------|-----------|-------------------|-----------|
| **Enfoque** | API FastAPI + MLOps | Data Drift Detection | Diferentes prioridades |
| **Archivos Modificados** | N/A | 37 archivos | - |
| **Archivos Eliminados** | N/A | 24 archivos | - |
| **Archivos Agregados** | N/A | 9 archivos | - |
| **Último Commit** | 94b224e | f3c8df7 | Ivan más reciente |
| **Commits Adelante** | 0 | 1 (drift detection) | Ivan tiene 1 más |

---

## 📁 ARCHIVOS ELIMINADOS en `ivan/features` (vs `ali`)

```
Eliminados: 24 archivos
├─ .dockerignore
├─ ARCHITECTURE.md
├─ DOCKER_DVC_GUIDE.md
├─ DOCUMENTATION_INDEX.md
├─ FAQ.md
├─ IMPLEMENTATION_SUMMARY.md
├─ SETUP_CHECKLIST.md
├─ api/README.md
├─ api/__init__.py
├─ api/config.py
├─ api/dependencies.py
├─ api/main.py
├─ api/routers/__init__.py
├─ api/routers/health.py
├─ api/routers/model_info.py
├─ api/routers/prediction.py
├─ api/schemas.py
├─ config/README.md
├─ config/docker.env.template
├─ config/dvc_config.yaml
├─ config/params.yaml
├─ Dockerfile.api
├─ requirements-api.txt
└─ tests/test_api.py
```

**IMPACTO:** Ivan ELIMINÓ completamente la capa API FastAPI. No hay servidor de predicciones en su rama.

---

## 📁 ARCHIVOS AGREGADOS en `ivan/features` (vs `ali`)

```
Agregados: 9 archivos
├─ MLproject (MLflow project config)
├─ python_env.yaml (Conda environment)
├─ docker-run.ps1 (Windows Docker script)
├─ docker-run.sh (Linux Docker script)
├─ scripts/compare_datasets.py (Data comparison)
├─ scripts/detect_drift.py (Drift detection)
├─ scripts/dvc_add_data.ps1 (Windows DVC script)
├─ scripts/dvc_add_data.sh (Linux DVC script)
├─ scripts/dvc_pull_data.sh (DVC pull script)
├─ scripts/dvc_push_artifacts.sh (DVC push script)
├─ scripts/dvc_setup.ps1 (Windows DVC setup)
├─ scripts/dvc_setup.sh (Linux DVC setup)
├─ scripts/load_model.py (Model loading)
├─ scripts/simulate_drift.py (Drift simulation)
├─ scripts/version_models.sh (Model versioning)
├─ scripts/visualize_drift.py (Drift visualization)
├─ src/monitoring/__init__.py
├─ src/monitoring/drift_detector.py (Core drift detection)
├─ reports/drift/ (Drift reports)
│  ├─ drift_alerts.txt
│  └─ drift_report.json
└─ python_env.yaml
```

**IMPACTO:** Ivan AGREGÓ todo el sistema de detección de drift y monitoring.

---

## 📝 ARCHIVOS MODIFICADOS en ambas ramas

```
Modificados: 13 archivos
├─ .dvc/.gitignore
├─ .dvc/config (DVC remote config)
├─ .env.example
├─ Dockerfile (cambios en dependencies)
├─ README.md
├─ data/raw/obesity_estimation_modified.csv.dvc
├─ docker-compose.yml
├─ requirements.txt (o eliminado en Ivan)
└─ ... otros archivos de config
```

---

## 🎯 DIFERENCIAS CONCEPTUALES

### Rama `ali` - Enfoque: **API & Production**

**Características:**
```
✅ FastAPI Server completo
   ├─ /predict endpoint
   ├─ /model/info endpoints
   ├─ /health checks
   └─ Validación con Pydantic

✅ Documentación completa
   ├─ ARCHITECTURE.md
   ├─ DOCKER_DVC_GUIDE.md
   ├─ API/README.md
   └─ Setup guides

✅ Docker optimizado
   ├─ Dockerfile.api (ligero, ~150MB)
   └─ Dockerfile (pipeline pesado)

✅ Tests
   ├─ test_api.py
   └─ test_ml_pipeline.py
```

**Stack:**
- FastAPI + Uvicorn
- Pydantic para validación
- MLflow para tracking
- DVC para versionado

**Objetivo:** Producción con API lista para servir predicciones

---

### Rama `ivan/features` - Enfoque: **Monitoring & Drift Detection**

**Características:**
```
✅ Drift Detection completo
   ├─ drift_detector.py (core)
   ├─ detect_drift.py (script)
   ├─ simulate_drift.py (testing)
   └─ visualize_drift.py (plots)

✅ Data Drift Monitoring
   ├─ Comparación de datasets
   ├─ Reportes de drift
   ├─ Alertas de drift
   └─ Métricas de drift (PSI, KS)

✅ MLOps Scripts
   ├─ DVC setup (setup.sh)
   ├─ DVC push/pull
   ├─ Model versioning
   └─ Data comparison

✅ MLflow Integration
   ├─ MLproject config
   └─ python_env.yaml (Conda)
```

**Stack:**
- MLflow para tracking
- DVC para versionado
- Monitoring tools
- Drift detection (PSI, KS tests)

**Objetivo:** Monitoring en producción y detección de data drift

---

## 📊 TABLA COMPARATIVA DETALLADA

| Feature | `ali` | `ivan/features` | Ganador |
|---------|-------|-----------------|---------|
| **API FastAPI** | ✅ Completa | ❌ Eliminada | ali |
| **Drift Detection** | ❌ No | ✅ Completa | ivan |
| **Documentación** | ✅ Extensiva | ⚠️ Minimal | ali |
| **Tests** | ✅ API + ML | ⚠️ Solo ML | ali |
| **Dockerfile.api** | ✅ Optimizado | ❌ Eliminado | ali |
| **DVC Scripts** | ⚠️ Basic | ✅ Completos | ivan |
| **Monitoring** | ❌ No | ✅ Completo | ivan |
| **Model Serving** | ✅ Listo | ❌ No | ali |
| **Configuration** | ✅ YAML + env | ✅ YAML + Conda | tie |
| **MLflow Integration** | ✅ Básico | ✅ Avanzado | ivan |

---

## 🔄 Commits que las Diferencian

### Rama `ali` (últimos commits):
```
94b224e - feat: Add FastAPI serving layer for model inference
43d20df - feat: Implementación completa DVC + Docker + S3
```

### Rama `ivan/features` (últimos commits):
```
f3c8df7 - Data Drifting (NUEVO)
94b224e - feat: Add FastAPI serving layer for model inference
43d20df - feat: Implementación completa DVC + Docker + S3
```

Ivan tiene **1 commit más** que implementa drift detection completo.

---

## 🎯 ANÁLISIS DE DECISIÓN

### Si necesitas: **API en Producción**
→ Usa rama **`ali`**
- Servidor FastAPI listo
- Endpoints documentados
- Tests completos
- Dockerfile optimizado

### Si necesitas: **Monitoreo y Drift Detection**
→ Usa rama **`ivan/features`**
- Sistema de drift detection
- Alertas automáticas
- Visualizaciones
- MLOps scripts

### Si necesitas: **AMBOS**
→ Necesitas hacer un **MERGE estratégico**
```
Option 1: Merge ali INTO ivan/features
├─ Ventaja: Drift detection + API
└─ Desventaja: Puede haber conflictos

Option 2: Merge ivan/features INTO ali
├─ Ventaja: Drift detection + API
└─ Desventaja: Puede haber conflictos

Option 3: Create new branch combining both
├─ Mejor: ali + drift detection de ivan
└─ Fusion controlada de lo mejor de ambas
```

---

## 📋 ARCHIVOS CRÍTICOS DIFERENTES

### 1. **Dockerfile**

**`ali`:**
```dockerfile
FROM python:3.10-slim
COPY requirements.txt
RUN pip install -r requirements.txt
# Setup DVC, Git, AWS CLI
```

**`ivan/features`:**
```dockerfile
Modificado para Conda en lugar de pip
Cambios en dependencias del sistema
```

### 2. **docker-compose.yml**

**`ali`:**
- Servicios: dvc-pipeline, api, mlflow, test, shell
- API en puerto 8000

**`ivan/features`:**
- Diferente configuración de servicios
- Enfoque en pipeline en lugar de API

### 3. **DVC Pipeline**

**`ali`:**
```yaml
Stages: eda → preprocess → train → evaluate → visualize
Output: best_pipeline.joblib
```

**`ivan/features`:**
```yaml
Stages: eda → preprocess → train → evaluate → visualize → drift_detection
Output: best_pipeline.joblib + drift_report.json
```

---

## 🛠️ RECOMENDACIÓN FINAL

| Escenario | Recomendación |
|-----------|---------------|
| **Producción pura (serving)** | Usa `ali` |
| **MLOps + Monitoring** | Usa `ivan/features` |
| **Producción + Monitoring** | Merge ambas en rama nueva |
| **Desarrollo** | Crea rama desde `ali` o `ivan` |

---

## 📊 Resumen de Cambios

```
Total de cambios entre ramas:
├─ Archivos eliminados:  24 (toda la API)
├─ Archivos agregados:   9 (drift detection)
├─ Archivos modificados: 13 (configs)
└─ Total diferente:      46 archivos

Líneas de código (estimadas):
├─ ali:            ~8,000 líneas (con API)
├─ ivan/features:  ~7,500 líneas (con drift detection)
└─ Diferencia:     Cambio de enfoque, no de tamaño
```

---

## ¿Cuál Usar?

**Resumen:**
- **`ali`** = API lista para producción
- **`ivan/features`** = Monitoreo y drift detection
- **Ideal futuro** = Ambas características en una rama

¿Cuál enfoque prefieres para el proyecto?

