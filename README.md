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
```

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

