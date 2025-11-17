# Obesity ML Project - MLOps con DVC y Docker

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![DVC](https://img.shields.io/badge/DVC-3.30-orange.svg)](https://dvc.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![MLflow](https://img.shields.io/badge/MLflow-2.8-blue.svg)](https://mlflow.org/)

Proyecto MLOps del **Equipo 52** para clasificación de niveles de obesidad utilizando orquestación con **DVC** y contenedores **Docker**.

> 📚 **[Índice Completo de Documentación](DOCUMENTATION_INDEX.md)** - Navega toda la documentación del proyecto

## 🎯 Características Principales

- **Pipeline Orquestado con DVC**: Automatización completa del flujo ML (EDA → Preprocessing → Training → Evaluation)
- **Versionado desde Docker**: Control de versiones de datos y modelos directamente en contenedores
- **Configuración Centralizada**: Parámetros y configuraciones en archivos YAML
- **Tracking con MLflow**: Seguimiento de experimentos y métricas
- **Docker Compose**: Múltiples servicios para diferentes tareas del pipeline

## 🚀 Inicio Rápido

### 1. Prerequisitos

- Docker y Docker Compose instalados
- Credenciales de AWS S3 (o alternativa: GCS, Azure, local)
- Git configurado

### 2. Configuración

```bash
# Clonar el repositorio
git clone <repository-url>
cd Fase-2_Equipo52

# Configurar variables de entorno
cp config/docker.env.template .env

# Editar .env con tus credenciales
# Ejemplo mínimo requerido:
# AWS_ACCESS_KEY_ID=tu_key
# AWS_SECRET_ACCESS_KEY=tu_secret
# DVC_REMOTE_URL=s3://tu-bucket/dvc-storage
```

### 3. Ejecutar Pipeline Completo

```bash
# Construir y ejecutar el pipeline completo con DVC
docker-compose up dvc-pipeline

# Ver los resultados
docker-compose run --rm shell dvc metrics show
```

### 4. Ver Experimentos en MLflow

```bash
# Iniciar servidor MLflow
docker-compose up -d mlflow

# Acceder a http://localhost:5001
```

## 📁 Estructura del Proyecto

```
Fase-2_Equipo52/
├── config/                      # 📝 Configuraciones centralizadas
│   ├── params.yaml             # Parámetros del pipeline
│   ├── dvc_config.yaml         # Configuración de DVC
│   └── docker.env.template     # Template de variables de entorno
│
├── dvc.yaml                    # 🔄 Definición del pipeline DVC
├── docker-compose.yml          # 🐳 Orquestación de servicios
├── Dockerfile                  # 🐳 Imagen Docker del proyecto
│
├── data/
│   ├── raw/                    # Datos originales
│   ├── interim/                # Datos procesados
│   └── processed/              # Datos finales
│
├── models/                     # 🤖 Modelos entrenados
├── reports/                    # 📊 Reportes y visualizaciones
│   ├── figures/
│   └── metrics/
│
├── scripts/                    # 🔧 Scripts de ejecución
│   ├── dvc_docker_setup.sh    # Configurar DVC en Docker
│   ├── dvc_run_pipeline.sh    # Ejecutar pipeline completo
│   ├── run_eda.py             # Análisis exploratorio
│   └── run_ml.py              # Entrenamiento de modelos
│
├── src/                        # 💻 Código fuente
│   ├── data/                   # Procesamiento de datos
│   ├── models/                 # Modelos y entrenamiento
│   └── visualization/          # Visualizaciones
│
└── tests/                      # 🧪 Tests unitarios
```

## 🔧 Servicios Docker Disponibles

### `dvc-pipeline` (Principal)
Ejecuta el pipeline completo orquestado por DVC:
```bash
docker-compose up dvc-pipeline
```

### `dvc-pull`
Descarga datos/modelos versionados:
```bash
docker-compose up dvc-pull
```

### `dvc-push`
Sube datos/modelos al remote storage:
```bash
docker-compose up dvc-push
```

### `mlflow`
Servidor MLflow UI:
```bash
docker-compose up -d mlflow
# http://localhost:5001
```

### `api`
**🚀 NUEVO**: API de Inferencia FastAPI:
```bash
docker-compose up api
# http://localhost:8000/docs
```

Endpoints disponibles:
- `POST /predict` - Predicción individual
- `POST /predict/batch` - Predicción por lote
- `GET /health` - Health check
- `GET /model/info` - Información del modelo

**Ver documentación completa**: [api/README.md](api/README.md)

### `shell`
Shell interactivo para desarrollo:
```bash
docker-compose run --rm shell

# Comandos útiles:
dvc status          # Estado del pipeline
dvc dag             # Visualizar DAG
dvc metrics show    # Ver métricas
```

### `test`
Ejecutar tests unitarios:
```bash
docker-compose up test
```

### `simulate-drift`
Simular data drift (genera dataset con cambios en distribuciones):
```bash
docker-compose run --rm simulate-drift
```

### `detect-drift`
Detectar data drift y comparar performance:
```bash
docker-compose run --rm detect-drift
```

### `visualize-drift`
Generar visualizaciones de drift detection:
```bash
docker-compose run --rm visualize-drift
```

## 📊 Pipeline DVC

El pipeline está definido en `dvc.yaml` y consta de 5 etapas:

```
┌─────────┐    ┌─────────────┐    ┌─────────┐    ┌──────────┐    ┌───────────┐
│   EDA   │ -> │ Preprocessing│ -> │  Train  │ -> │ Evaluate │ -> │ Visualize │
└─────────┘    └─────────────┘    └─────────┘    └──────────┘    └───────────┘
```

### Etapas del Pipeline

1. **EDA**: Limpieza y análisis exploratorio de datos
2. **Preprocess**: Feature engineering (BMI), encoding, scaling
3. **Train**: Entrenamiento de múltiples modelos con validación cruzada
4. **Evaluate**: Evaluación del mejor modelo en datos de prueba
5. **Visualize**: Generación de reportes y visualizaciones

## 🎛️ Configuración de Parámetros

Todos los parámetros están centralizados en `config/params.yaml`:

```yaml
data:
  test_size: 0.2
  random_state: 42

models:
  algorithms:
    - logistic_regression
    - random_forest
    - xgboost

training:
  cv_folds: 5
  scoring: accuracy
```

Modificar estos parámetros re-ejecuta solo las etapas afectadas (gracias a DVC).

## 🔐 Versionado de Datos con DVC

### Agregar Datos a DVC

```bash
docker-compose run --rm shell bash scripts/dvc_version.sh add-data
```

### Subir al Remote Storage

```bash
docker-compose up dvc-push
```

### Descargar desde Remote Storage

```bash
docker-compose up dvc-pull
```

## 📈 Monitoreo y Métricas

### Ver Métricas con DVC

```bash
docker-compose run --rm shell dvc metrics show
```

### Ver Experimentos en MLflow

```bash
docker-compose up -d mlflow
# Abrir http://localhost:5001
```

### Comparar Versiones

```bash
docker-compose run --rm shell dvc metrics diff
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
docker-compose up test

# Ejecutar tests específicos
docker-compose run --rm test pytest tests/test_ml_pipeline.py -v

# Tests del API
docker-compose run --rm test pytest tests/test_api.py -v
```

## 🚀 API de Inferencia (FastAPI)

### Características

El proyecto incluye una **API REST completa** construida con **FastAPI** para realizar predicciones en tiempo real:

- ✅ **Endpoints RESTful** para predicción individual (`POST /predict`) y por lote (`POST /predict/batch`)
- ✅ **Validación automática** de entrada con Pydantic
- ✅ **Documentación interactiva** con Swagger/OpenAPI en `/docs`
- ✅ **Health checks** para monitoring en `GET /health`
- ✅ **Información del modelo** en `GET /model/info`
- ✅ **Handling de errores** robusto con respuestas JSON
- ✅ **CORS habilitado** para acceso desde cualquier origen
- ✅ **Logging completo** de predicciones

### Inicio Rápido

```bash
# Opción 1: Levantar el servicio API con Docker Compose
docker-compose up api

# Opción 2: Ejecutar localmente (si tienes las dependencias instaladas)
cd Fase-2_Equipo52
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Acceder a la API:**
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc
- API raíz: http://localhost:8000/

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Health check del servicio |
| `GET` | `/model/info` | Información del modelo (versión, accuracy, clases) |
| `POST` | `/predict` | Predicción individual |
| `POST` | `/predict/batch` | Predicción por lote (múltiples muestras) |

### Ejemplo de Uso: Predicción Individual

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 25.0,
    "Height": 1.75,
    "Weight": 85.0,
    "Gender": "Male",
    "FCVC": 2.0,
    "NCP": 3.0,
    "CAEC": "Sometimes",
    "CH2O": 2.5,
    "FAF": 1.5,
    "TUE": 1.0,
    "MTRANS": "Automobile",
    "family_history_with_overweight": "yes",
    "FAVC": "no",
    "SCC": "no"
  }'
```

**Respuesta esperada:**

```json
{
  "prediction": "Overweight_Level_II",
  "confidence": null,
  "features_received": {
    "Age": 25.0,
    "Height": 1.75,
    "Weight": 85.0,
    "Gender": "Male",
    "FCVC": 2.0,
    "NCP": 3.0,
    "CAEC": "Sometimes",
    "CH2O": 2.5,
    "FAF": 1.5,
    "TUE": 1.0,
    "MTRANS": "Automobile",
    "family_history_with_overweight": "yes",
    "FAVC": "no",
    "SCC": "no"
  },
  "model_name": "XGBoost_SMOTE",
  "model_version": "1.0.0"
}
```

### Ejemplo: Predicción Batch

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [
      {
        "Age": 25.0,
        "Height": 1.75,
        "Weight": 85.0,
        "Gender": "Male",
        "FCVC": 2.0,
        "NCP": 3.0,
        "CAEC": "Sometimes",
        "CH2O": 2.5,
        "FAF": 1.5,
        "TUE": 1.0,
        "MTRANS": "Automobile",
        "family_history_with_overweight": "yes",
        "FAVC": "no",
        "SCC": "no"
      }
    ]
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Información del Modelo

```bash
curl http://localhost:8000/model/info
```

**Respuesta:**

```json
{
  "model_name": "XGBoost_SMOTE",
  "model_version": "1.0.0",
  "accuracy": 0.975,
  "classes": [
    "Insufficient_Weight",
    "Normal_Weight",
    "Overweight_Level_I",
    "Overweight_Level_II",
    "Obesity_Type_I",
    "Obesity_Type_II",
    "Obesity_Type_III"
  ],
  "features_required": 13,
  "deployment_date": "2024-01-15"
}
```

### Versionado del Modelo y Artefactos

```
Modelo guardado en:
  models/best_pipeline.joblib (artefacto principal)
  models/model_metadata.joblib (metadata)

Información de versión:
  Versión del modelo: v1.0.0
  Framework: XGBoost + SMOTE
  Accuracy: ~97%
  Test size: 20%
```

### Schema de Validación (Pydantic)

El endpoint `/predict` valida automáticamente:

```python
class ObesityFeatures(BaseModel):
    Age: float  # 14-100 años
    Height: float  # 1.0-2.5 metros
    Weight: float  # 20-200 kg
    Gender: str  # "Female" o "Male"
    FCVC: float  # 1-3 (Frecuencia consumo verduras)
    NCP: float  # 1-4 (Número comidas principales)
    CAEC: str  # "no", "Sometimes", "Frequently", "Always"
    CH2O: float  # 1-3 (Consumo agua diario)
    FAF: float  # 0-3 (Frecuencia actividad física)
    TUE: float  # 0-2 (Tiempo usando tecnología)
    MTRANS: str  # Tipo de transporte
    family_history_with_overweight: str  # "yes" o "no"
    FAVC: str  # "yes" o "no" (Comida calórica frecuente)
    SCC: str  # "yes" o "no" (Bebidas calóricas)
```

Errores de validación retornan `HTTP 422` con detalles específicos.

## 🔍 Data Drift Detection

El proyecto incluye un **sistema completo de detección de data drift** para monitorear cambios en la distribución de datos que afectan el desempeño del modelo.

### Características

- ✅ **PSI (Population Stability Index)**: Detecta cambios en distribuciones de features
- ✅ **Tests Estadísticos**: Comparación con KS test y Mann-Whitney U
- ✅ **Monitoreo de Performance**: Compara métricas (Accuracy, Precision, Recall, F1)
- ✅ **Sistema de Alertas**: Umbrales configurables (PSI > 0.2, Accuracy degradation > 5%)
- ✅ **Visualizaciones**: Gráficos comparativos y heatmaps

### Flujo de Drift Detection

```bash
# 1. Simular drift (genera dataset con cambios controlados)
docker compose run --rm simulate-drift

# 2. Detectar drift y comparar performance
docker compose run --rm detect-drift

# 3. Generar visualizaciones
docker compose run --rm visualize-drift
```

### Resultados Generados

Después de ejecutar el flujo, encontrarás:

- **Dataset con drift**: `data/interim/dataset_with_drift.csv`
- **Reporte JSON**: `reports/drift/drift_report.json`
- **Alertas**: `reports/drift/drift_alerts.txt`
- **Visualizaciones**:
  - `reports/figures/10_drift_distributions.png` - Distribuciones comparadas
  - `reports/figures/11_drift_performance_comparison.png` - Comparación de métricas
  - `reports/figures/12_drift_psi_heatmap.png` - Heatmap de PSI

### Umbrales y Alertas

El sistema utiliza los siguientes umbrales profesionales:

- **PSI > 0.2**: Alerta de drift significativo en feature
- **PSI > 0.5**: Alerta crítica de drift
- **Accuracy degradation > 5%**: Warning de degradación
- **Accuracy degradation > 10%**: Alerta crítica (recomienda retrain)

### Interpretación de Resultados

**Ejemplo de resultados:**
- Baseline Accuracy: 99.3%
- Current Accuracy: 65.4%
- **Degradación: -34.1%** → Alerta CRÍTICA

**¿Es malo que baje el accuracy?**
No, es **esperado y demuestra que el sistema funciona**. La degradación indica que:
1. Los datos han cambiado (drift detectado)
2. El modelo necesita retrenarse con datos actuales
3. El sistema de monitoreo está funcionando correctamente

**Ver resumen completo**: [RESUMEN_DRIFT_DETECTION.md](RESUMEN_DRIFT_DETECTION.md)

## 🐳 Comandos Docker Directos

Además de `docker-compose`, puedes usar comandos directos de Docker:

### Construir Imagen

```bash
# Construir imagen del servicio
docker build -t ml-service:latest .

# Construir con tag versionado
docker build -t ml-service:v1.0.0 .
docker build -t ml-service:v1.0.0 -t ml-service:latest .
```

### Ejecutar Contenedor

```bash
# Ejecutar contenedor del servicio API
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  ml-service:latest

# Ejecutar con tag específico
docker run -p 8000:8000 ml-service:v1.0.0
```

### Publicar en DockerHub (Opcional)

```bash
# Login a DockerHub
docker login

# Tag para DockerHub
docker tag ml-service:latest tu-usuario/ml-service:v1.0.0
docker tag ml-service:latest tu-usuario/ml-service:latest

# Push a DockerHub
docker push tu-usuario/ml-service:v1.0.0
docker push tu-usuario/ml-service:latest
```

### Tags Versionados Recomendados

- `v1.0.0` - Versión inicial
- `v1.1.0` - Nuevas features
- `v1.0.1` - Bug fixes
- `latest` - Última versión estable

## 📚 Documentación Adicional

- [Guía Completa Docker + DVC](DOCKER_DVC_GUIDE.md)
- [FAQ - Preguntas Frecuentes](FAQ.md)
- [Checklist de Setup](SETUP_CHECKLIST.md)
- [Arquitectura del Sistema](ARCHITECTURE.md)

## 🔄 Flujo de Trabajo Típico

### Desarrollo de Nuevas Features

1. Modificar código o parámetros
2. Probar en shell interactivo: `docker-compose run --rm shell`
3. Ejecutar pipeline: `docker-compose up dvc-pipeline`
4. Versionar cambios: `docker-compose up dvc-push`

### Reproducir Experimentos

1. Pull de datos: `docker-compose up dvc-pull`
2. Ejecutar pipeline: `docker-compose up dvc-pipeline`
3. Ver métricas: `docker-compose run --rm shell dvc metrics show`

## 🐛 Troubleshooting

### DVC Remote no configurado

```bash
# Verificar .env
cat .env | grep DVC_REMOTE

# Re-configurar
docker-compose run --rm shell bash scripts/dvc_docker_setup.sh
```

### Reconstruir contenedores

```bash
docker-compose build --no-cache
docker-compose up dvc-pipeline
```

## 🤝 Equipo

**Equipo 52 - Proyecto MLOps**

- Clasificación de Niveles de Obesidad
- Fase 2: Orquestación con DVC y Docker

## 📄 Licencia

Este proyecto es parte del curso de MLOps y está disponible para fines educativos.

## 🔗 Referencias

- [DVC Documentation](https://dvc.org/doc)
- [Docker Documentation](https://docs.docker.com/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Scikit-learn](https://scikit-learn.org/)
