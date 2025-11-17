# 🔍 Guía Completa: Ejecución de Drift Detection

Este documento explica cómo ejecutar el sistema de detección de drift usando Docker, DVC y scripts directos.

---

## 📋 Tabla de Contenidos

1. [Ejecución Rápida](#ejecución-rápida)
2. [Con Docker](#con-docker)
3. [Con DVC](#con-dvc)
4. [Scripts Directos](#scripts-directos)
5. [Casos de Uso](#casos-de-uso)

---

## ⚡ Ejecución Rápida

### Opción 1: Script Directo (Más Rápido)
```bash
# Simular drift
python scripts/simulate_drift.py

# Detectar drift
python scripts/detect_drift.py

# Visualizar drift
python scripts/visualize_drift.py
```

### Opción 2: Docker Compose (Aislado)
```bash
# Ejecutar todo el pipeline con drift
docker-compose up simulate-drift detect-drift visualize-drift

# O ejecutar solo detección
docker-compose up detect-drift
```

### Opción 3: DVC Pipeline (Con Versionado)
```bash
# Ejecutar solo drift
dvc repro simulate_drift detect_drift visualize_drift

# O ejecutar etapa específica
dvc repro detect_drift
```

---

## 🐳 Con Docker

### Servicios Disponibles en docker-compose.yml

#### 1. **Simular Drift**
```yaml
simulate-drift:
  image: obesity-ml-project:latest
  command: python scripts/simulate_drift.py
  volumes:
    - ./data:/app/data
    - ./reports:/app/reports
  depends_on:
    - dvc-pull
    - eda-pipeline
```

**Ejecutar:**
```bash
docker-compose up simulate-drift
```

**Salida esperada:**
```
obesity-ml-simulate-drift | Shifting Age distribution:
obesity-ml-simulate-drift |   Baseline mean: 45.32
obesity-ml-simulate-drift |   New mean: 49.85
obesity-ml-simulate-drift | ✓ Drift simulation completed successfully!
obesity-ml-simulate-drift | ✓ Drifted dataset saved to: data/interim/dataset_with_drift.csv
```

---

#### 2. **Detectar Drift**
```yaml
detect-drift:
  image: obesity-ml-project:latest
  command: python scripts/detect_drift.py
  volumes:
    - ./data:/app/data
    - ./models:/app/models
    - ./reports:/app/reports
  depends_on:
    - dvc-pull
    - eda-pipeline
    - ml-pipeline
    - simulate-drift
```

**Ejecutar:**
```bash
docker-compose up detect-drift
```

**Salida esperada:**
```
obesity-ml-detect-drift | DATA DRIFT DETECTION
obesity-ml-detect-drift | ======================================================================
obesity-ml-detect-drift | 1. Loading datasets...
obesity-ml-detect-drift | Baseline dataset: (2111, 16)
obesity-ml-detect-drift | Drifted dataset: (2111, 16)
obesity-ml-detect-drift |
obesity-ml-detect-drift | 2. Loading trained model...
obesity-ml-detect-drift | Model: best_pipeline
obesity-ml-detect-drift | Baseline accuracy: 0.9930
obesity-ml-detect-drift |
obesity-ml-detect-drift | 5. Detecting feature drift...
obesity-ml-detect-drift | DRIFT DETECTION SUMMARY
obesity-ml-detect-drift | ======================================================================
obesity-ml-detect-drift |
obesity-ml-detect-drift | Features analyzed: 8
obesity-ml-detect-drift | Features with drift: 8
obesity-ml-detect-drift |
obesity-ml-detect-drift | Alerts:
obesity-ml-detect-drift |   Critical: 7
obesity-ml-detect-drift |   Warnings: 2
obesity-ml-detect-drift |
obesity-ml-detect-drift | ✓ Drift detection completed successfully!
obesity-ml-detect-drift | ✓ Reports saved to: reports/drift
```

---

#### 3. **Visualizar Drift**
```yaml
visualize-drift:
  image: obesity-ml-project:latest
  command: python scripts/visualize_drift.py
  volumes:
    - ./data:/app/data
    - ./reports:/app/reports
  depends_on:
    - detect-drift
```

**Ejecutar:**
```bash
docker-compose up visualize-drift
```

**Salida esperada:**
```
obesity-ml-visualize-drift | GENERATING DRIFT VISUALIZATIONS
obesity-ml-visualize-drift | ======================================================================
obesity-ml-visualize-drift |
obesity-ml-visualize-drift | 1. Creating feature distribution plots...
obesity-ml-visualize-drift | Distribution plot saved to: reports/figures/10_drift_distributions.png
obesity-ml-visualize-drift |
obesity-ml-visualize-drift | 2. Creating performance comparison plot...
obesity-ml-visualize-drift | Performance comparison plot saved to: reports/figures/11_drift_performance_comparison.png
obesity-ml-visualize-drift |
obesity-ml-visualize-drift | 3. Creating PSI heatmap...
obesity-ml-visualize-drift | PSI heatmap saved to: reports/figures/12_drift_psi_heatmap.png
obesity-ml-visualize-drift |
obesity-ml-visualize-drift | ✓ All visualizations generated successfully!
obesity-ml-visualize-drift | ✓ Figures saved to: reports/figures/
```

---

### Ejecutar Todo en Una Sola Línea

```bash
# Simular → Detectar → Visualizar (en secuencia)
docker-compose up simulate-drift detect-drift visualize-drift

# O con logs filtrados
docker-compose up simulate-drift detect-drift visualize-drift --no-deps

# O en background
docker-compose up -d simulate-drift detect-drift visualize-drift
docker-compose logs -f detect-drift  # Ver logs en tiempo real
```

---

### Servicios Requeridos Antes de Ejecutar Drift

```bash
# Opción 1: Ejecutar todo desde cero
docker-compose up

# Opción 2: Ejecutar solo lo necesario para drift
docker-compose up dvc-pull eda-pipeline ml-pipeline simulate-drift detect-drift visualize-drift

# Opción 3: En paralelo (más rápido)
docker-compose up -d dvc-pull
docker-compose up -d eda-pipeline ml-pipeline
docker-compose up -d simulate-drift detect-drift visualize-drift
```

---

## 🔄 Con DVC

### Comando DVC

**Ejecutar etapas específicas:**
```bash
# Solo simulación de drift
dvc repro simulate_drift

# Solo detección
dvc repro detect_drift

# Solo visualización
dvc repro visualize_drift

# Todo el pipeline de drift
dvc repro simulate_drift detect_drift visualize_drift

# Etapas específicas en orden
dvc repro -s simulate_drift -s detect_drift -s visualize_drift
```

**Ejecutar todo el pipeline ML:**
```bash
# Ejecuta: eda → preprocess → train → evaluate → visualize → simulate_drift → detect_drift → visualize_drift
dvc repro
```

---

### Configuración DVC en dvc.yaml

```yaml
stages:
  # Stages existentes...
  eda:
    cmd: python scripts/run_eda.py --input ${data.raw_path} --output ${data.interim_path}
    deps: [scripts/run_eda.py, data/raw/obesity_estimation_modified.csv, ...]
    outs:
      - ${data.interim_path}:
          cache: true
          persist: true

  # ... train, evaluate, visualize ...

  # NUEVOS: Drift Detection
  simulate_drift:
    cmd: python scripts/simulate_drift.py
    deps:
      - scripts/simulate_drift.py
      - ${data.interim_path}
      - src/utils/config.py
    outs:
      - data/interim/dataset_with_drift.csv:
          cache: true
    desc: "Simula data drift modificando distribuciones"

  detect_drift:
    cmd: python scripts/detect_drift.py
    deps:
      - scripts/detect_drift.py
      - ${data.interim_path}
      - data/interim/dataset_with_drift.csv
      - ${models.output_dir}/best_pipeline.joblib
      - src/monitoring/drift_detector.py
    outs:
      - reports/drift/drift_report.json
      - reports/drift/drift_alerts.txt
    desc: "Detección de data drift"

  visualize_drift:
    cmd: python scripts/visualize_drift.py
    deps:
      - scripts/visualize_drift.py
      - data/interim/dataset_with_drift.csv
      - reports/drift/drift_report.json
    outs:
      - reports/figures/10_drift_distributions.png
      - reports/figures/11_drift_performance_comparison.png
      - reports/figures/12_drift_psi_heatmap.png
    desc: "Visualización de data drift"
```

---

### Ver el DAG del Pipeline

```bash
# Ver todo el pipeline
dvc dag

# Ver solo drift
dvc dag --target visualize_drift

# Ver dependencias
dvc status
```

---

## 📝 Scripts Directos

### 1. Simular Drift

```bash
python scripts/simulate_drift.py
```

**Opciones en el código:**
```python
simulate_drift(
    input_path=REFACTORED_CLEAN_DATA_PATH,
    output_path=INTERIM_DATA_DIR / "dataset_with_drift.csv",
    age_shift_pct=0.10,           # 10% shift en Age
    weight_shift_pct=0.15,        # 15% shift en Weight
    height_shift_pct=0.05,        # 5% shift en Height
    add_noise=True,               # 3% noise en otros features
    random_state=42               # Reproducibilidad
)
```

**Salidas:**
- `data/interim/dataset_with_drift.csv` - Dataset con drift simulado

---

### 2. Detectar Drift

```bash
python scripts/detect_drift.py
```

**Requisitos previos:**
- ✅ Dataset limpio: `data/interim/dataset_limpio_refactored.csv`
- ✅ Modelo entrenado: `models/best_pipeline.joblib`
- ✅ Metadata: `models/model_metadata.joblib`
- ✅ Dataset con drift: `data/interim/dataset_with_drift.csv`

**Salidas:**
```
reports/drift/
├── drift_report.json        # Reporte técnico completo (JSON)
└── drift_alerts.txt         # Alertas legibles (TXT)
```

**Contenido drift_report.json:**
```json
{
  "baseline_dataset": "...",
  "drifted_dataset": "...",
  "model_name": "best_pipeline",
  "baseline_metrics": {
    "accuracy": 0.9930,
    "precision": 0.9935,
    "recall": 0.9930,
    "f1": 0.9930
  },
  "current_metrics": {
    "accuracy": 0.6544,
    "precision": 0.6850,
    "recall": 0.6544,
    "f1": 0.6660
  },
  "feature_drift": {
    "Age": {
      "psi": 0.577,
      "psi_alert": true,
      "ks_significant": true,
      "mean_shift_pct": 9.85,
      "drift_severity": "medium"
    },
    "Weight": {
      "psi": 0.577,
      "psi_alert": true,
      "ks_significant": true,
      "mean_shift_pct": 15.23,
      "drift_severity": "medium"
    },
    ...
  },
  "alerts": [
    {
      "type": "feature_drift",
      "feature": "Age",
      "level": "warning",
      "message": "Feature 'Age' shows significant drift (PSI: 0.577)",
      "psi": 0.577
    },
    {
      "type": "performance_degradation",
      "metric": "accuracy",
      "level": "critical",
      "message": "Critical degradation in accuracy: 34.13% drop",
      "degradation_pct": 34.13,
      "baseline": 0.9930,
      "current": 0.6544
    },
    ...
  ]
}
```

---

### 3. Visualizar Drift

```bash
python scripts/visualize_drift.py
```

**Requisitos previos:**
- ✅ Dataset limpio: `data/interim/dataset_limpio_refactored.csv`
- ✅ Dataset con drift: `data/interim/dataset_with_drift.csv`
- ✅ Reporte de drift: `reports/drift/drift_report.json`

**Salidas (3 PNG files):**
```
reports/figures/
├── 10_drift_distributions.png          # Comparación de distribuciones
├── 11_drift_performance_comparison.png # Degradación de métricas
└── 12_drift_psi_heatmap.png            # PSI por feature
```

---

## 🎯 Casos de Uso

### Caso 1: Testing Local (Desarrollo)

```bash
# Rápido y directo
python scripts/simulate_drift.py
python scripts/detect_drift.py
python scripts/visualize_drift.py

# Ver resultados
cat reports/drift/drift_alerts.txt
open reports/figures/10_drift_distributions.png
```

**Tiempo estimado:** 2-3 minutos

---

### Caso 2: CI/CD Pipeline (GitHub Actions)

```yaml
name: Drift Detection

on: [push, pull_request]

jobs:
  drift-detection:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run DVC pipeline
        run: |
          dvc pull
          dvc repro detect_drift

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: drift-reports
          path: reports/drift/
```

---

### Caso 3: Production Monitoring (Scheduled)

```bash
# Corntab (cada día a las 2 AM)
0 2 * * * cd /app && docker-compose up detect-drift visualize-drift

# O con supervisord
[program:drift-detection]
command=python /app/scripts/detect_drift.py
directory=/app
autostart=false
autorestart=false
```

---

### Caso 4: Integración con API

```python
# api/routers/monitoring.py
from fastapi import APIRouter, HTTPException
from src.monitoring.drift_detector import DriftDetector
import pandas as pd

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.post("/detect-drift")
async def detect_drift_endpoint(baseline_path: str, current_path: str):
    """
    Detect drift between two datasets
    """
    try:
        df_baseline = pd.read_csv(baseline_path)
        df_current = pd.read_csv(current_path)

        detector = DriftDetector()
        report = detector.detect_drift(
            baseline_data=df_baseline,
            current_data=df_current,
            baseline_metrics={...},
            current_metrics={...}
        )

        return {
            "status": "success",
            "drift_detected": len(report['alerts']) > 0,
            "total_alerts": report['summary']['total_alerts'],
            "critical_alerts": report['summary']['critical_alerts']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Caso 5: Monitoreo en Tiempo Real (Streaming)

```python
# scripts/monitor_drift_continuous.py
import time
import json
from datetime import datetime
from src.monitoring.drift_detector import DriftDetector

def continuous_monitoring(baseline_path, check_interval=3600):
    """
    Monitor drift continuously
    Check every hour for new data
    """
    detector = DriftDetector()

    while True:
        try:
            df_baseline = pd.read_csv(baseline_path)
            df_current = pd.read_csv("data/production/current_data.csv")

            report = detector.detect_drift(
                baseline_data=df_baseline,
                current_data=df_current,
                baseline_metrics={...},
                current_metrics={...}
            )

            # Log results
            with open("logs/drift_monitoring.log", "a") as f:
                f.write(f"[{datetime.now()}] Alerts: {report['summary']['total_alerts']}\n")

            # Send alerts if critical
            if report['summary']['critical_alerts'] > 0:
                send_alert_email(report)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(check_interval)  # Check every hour
```

---

## 📊 Flujo Recomendado

```
┌─────────────────────────────────────────────────────────┐
│         1. Entrenar Modelo (una sola vez)              │
│   docker-compose up dvc-pull eda-pipeline ml-pipeline  │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│    2. Simular Drift (para testing)                     │
│      python scripts/simulate_drift.py                   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│    3. Detectar Drift (análisis estadístico)            │
│      python scripts/detect_drift.py                     │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│    4. Visualizar Drift (reportes gráficos)             │
│      python scripts/visualize_drift.py                  │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│    5. Revisar Resultados                               │
│  ├─ reports/drift/drift_report.json                    │
│  ├─ reports/drift/drift_alerts.txt                     │
│  ├─ reports/figures/10_drift_distributions.png         │
│  ├─ reports/figures/11_drift_performance_comparison.png│
│  └─ reports/figures/12_drift_psi_heatmap.png           │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Ejecución

### Antes de ejecutar detect_drift

- [ ] Dataset limpio existe: `data/interim/dataset_limpio_refactored.csv`
- [ ] Modelo entrenado existe: `models/best_pipeline.joblib`
- [ ] Metadata existe: `models/model_metadata.joblib`
- [ ] Dataset con drift existe: `data/interim/dataset_with_drift.csv`
- [ ] Directorio reports/drift existe (se crea automáticamente)

### Después de ejecutar

- [ ] Revisar `reports/drift/drift_report.json`
- [ ] Revisar `reports/drift/drift_alerts.txt`
- [ ] Revisar las 3 imágenes PNG en `reports/figures/`
- [ ] Verificar umbrales de PSI y performance

---

## 🔧 Troubleshooting

### Error: FileNotFoundError

```
Error: Baseline dataset not found: data/interim/dataset_limpio_refactored.csv
```

**Solución:**
```bash
# Ejecutar EDA pipeline primero
python scripts/run_eda.py
# O con Docker
docker-compose up eda-pipeline
# O con DVC
dvc repro eda
```

---

### Error: Model not found

```
Error: Model not found: models/best_pipeline.joblib
```

**Solución:**
```bash
# Ejecutar ML pipeline
python scripts/run_ml.py
# O con Docker
docker-compose up ml-pipeline
# O con DVC
dvc repro train
```

---

### Error: Dataset with drift not found

```
Error: Drifted dataset not found: data/interim/dataset_with_drift.csv
```

**Solución:**
```bash
# Simular drift primero
python scripts/simulate_drift.py
# O con Docker
docker-compose up simulate-drift
# O con DVC
dvc repro simulate_drift
```

---

## 📚 Archivos Relacionados

- [MERGE_DRIFT_DETECTION.md](MERGE_DRIFT_DETECTION.md) - Detalles del merge
- [dvc.yaml](dvc.yaml) - Configuración DVC con drift stages
- [docker-compose.yml](docker-compose.yml) - Servicios Docker disponibles
- [requirements.txt](requirements.txt) - Dependencias (incluye scipy)

---

**¡Listo para ejecutar drift detection!** 🚀
