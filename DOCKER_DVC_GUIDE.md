# Guía de Uso - Orquestación DVC con Docker

## 📋 Descripción General

Este proyecto utiliza **DVC (Data Version Control)** para orquestar el pipeline completo de Machine Learning, y **Docker** para ejecutar todo en contenedores. El versionado de datos y modelos se realiza **desde Docker**, no localmente.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              dvc-pipeline (Principal)                 │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │  │
│  │  │   EDA   │→ │ Preproc │→ │  Train  │→ │ Evaluate│ │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────┐  ┌───────────┐  ┌──────────┐              │
│  │ dvc-pull  │  │ dvc-push  │  │  mlflow  │              │
│  └───────────┘  └───────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
    ┌──────────┐              ┌──────────────┐
    │ S3/Cloud │              │ Local Files  │
    │  Storage │              │ (Volumenes)  │
    └──────────┘              └──────────────┘
```

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
# Copiar el template y editarlo con tus credenciales
cp config/docker.env.template .env

# Editar .env con tus credenciales de AWS/Cloud
# Ejemplo mínimo:
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
DVC_REMOTE_URL=s3://tu-bucket/dvc-storage
```

### 2. Ejecutar Pipeline Completo

```bash
# Ejecuta todo el pipeline orquestado por DVC
docker-compose up dvc-pipeline

# O en modo detached
docker-compose up -d dvc-pipeline
```

### 3. Ver Resultados

```bash
# Ver logs
docker-compose logs -f dvc-pipeline

# Abrir shell interactivo
docker-compose run --rm shell

# Dentro del shell:
dvc metrics show
dvc dag
```

## 📦 Servicios Disponibles

### Servicio Principal: `dvc-pipeline`
Ejecuta el pipeline completo orquestado por DVC:
1. **EDA**: Limpieza y análisis exploratorio
2. **Preprocess**: Feature engineering
3. **Train**: Entrenamiento de modelos
4. **Evaluate**: Evaluación del mejor modelo
5. **Visualize**: Generación de reportes

```bash
docker-compose up dvc-pipeline
```

### Servicio: `dvc-pull`
Descarga datos/modelos versionados desde el remote storage:

```bash
docker-compose up dvc-pull
```

### Servicio: `dvc-push`
Sube datos/modelos al remote storage:

```bash
docker-compose up dvc-push
```

### Servicio: `mlflow`
Servidor MLflow UI para tracking de experimentos:

```bash
docker-compose up -d mlflow
# Acceder a http://localhost:5001
```

### Servicio: `shell`
Shell interactivo para desarrollo y debugging:

```bash
docker-compose run --rm shell

# Comandos útiles dentro del shell:
dvc status          # Ver estado del pipeline
dvc repro          # Re-ejecutar pipeline
dvc dag            # Ver DAG del pipeline
dvc metrics show   # Ver métricas
```

### Servicio: `test`
Ejecutar tests unitarios:

```bash
docker-compose up test
```

## 🔧 Comandos Útiles

### Gestión de Pipeline

```bash
# Ver estado del pipeline
docker-compose run --rm shell dvc status

# Ejecutar pipeline completo
docker-compose up dvc-pipeline

# Re-ejecutar solo una etapa
docker-compose run --rm shell dvc repro evaluate

# Ver DAG (grafo de dependencias)
docker-compose run --rm shell dvc dag

# Ver métricas
docker-compose run --rm shell dvc metrics show
```

### Gestión de Datos

```bash
# Descargar datos desde remote
docker-compose up dvc-pull

# Subir datos/modelos al remote
docker-compose up dvc-push

# Agregar nuevos archivos a DVC
docker-compose run --rm shell dvc add data/raw/nuevo_archivo.csv

# Commit cambios en DVC
docker-compose run --rm shell bash -c "dvc add data/raw/*.csv && git add data/raw/*.csv.dvc"
```

### Desarrollo y Debugging

```bash
# Entrar al contenedor en modo interactivo
docker-compose run --rm shell

# Ver logs de un servicio
docker-compose logs -f dvc-pipeline

# Ejecutar un script específico
docker-compose run --rm shell python scripts/run_eda.py

# Ejecutar tests
docker-compose up test
```

## 📁 Estructura del Proyecto

```
.
├── config/                     # Configuraciones centralizadas
│   ├── params.yaml            # Parámetros del pipeline
│   ├── dvc_config.yaml        # Configuración de DVC
│   └── docker.env.template    # Template de variables de entorno
│
├── dvc.yaml                   # Definición del pipeline DVC
├── dvc.lock                   # Lock file de DVC (generado)
│
├── docker-compose.yml         # Orquestación de servicios Docker
├── Dockerfile                 # Imagen Docker del proyecto
│
├── data/
│   ├── raw/                   # Datos originales
│   ├── interim/               # Datos procesados
│   └── processed/             # Datos finales
│
├── models/                    # Modelos entrenados
├── reports/                   # Reportes y visualizaciones
│   ├── figures/
│   └── metrics/
│
├── scripts/                   # Scripts de ejecución
│   ├── dvc_docker_setup.sh   # Configurar DVC en Docker
│   ├── dvc_run_pipeline.sh   # Ejecutar pipeline completo
│   └── ...
│
└── src/                       # Código fuente
    ├── data/
    ├── models/
    └── visualization/
```

## 🔐 Configuración de Remote Storage

### Opción 1: AWS S3

```bash
# En .env:
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
DVC_REMOTE_URL=s3://tu-bucket/dvc-storage
DVC_REMOTE_NAME=myremote
```

### Opción 2: Google Cloud Storage

```bash
# En .env:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DVC_REMOTE_URL=gs://tu-bucket/dvc-storage
DVC_REMOTE_NAME=myremote
```

### Opción 3: Azure Blob Storage

```bash
# En .env:
AZURE_STORAGE_CONNECTION_STRING=tu_connection_string
DVC_REMOTE_URL=azure://tu-container/dvc-storage
DVC_REMOTE_NAME=myremote
```

### Opción 4: Local/NFS (solo para desarrollo)

```bash
# En .env:
DVC_REMOTE_URL=/tmp/dvc-storage
DVC_REMOTE_NAME=local
```

## 🎯 Flujo de Trabajo Típico

### Desarrollo de Nuevas Features

1. **Modificar código/parámetros**:
   ```bash
   # Editar config/params.yaml o src/
   ```

2. **Probar localmente en shell**:
   ```bash
   docker-compose run --rm shell
   python scripts/run_eda.py
   exit
   ```

3. **Ejecutar pipeline completo**:
   ```bash
   docker-compose up dvc-pipeline
   ```

4. **Versionar cambios**:
   ```bash
   docker-compose up dvc-push
   ```

### Reproducir Experimentos

1. **Descargar datos versionados**:
   ```bash
   docker-compose up dvc-pull
   ```

2. **Ejecutar pipeline específico**:
   ```bash
   docker-compose run --rm shell dvc repro train
   ```

3. **Comparar métricas**:
   ```bash
   docker-compose run --rm shell dvc metrics diff
   ```

## 📊 Monitoreo y Visualización

### MLflow UI

```bash
# Iniciar servidor MLflow
docker-compose up -d mlflow

# Acceder a http://localhost:5001
```

### Métricas de DVC

```bash
# Ver métricas actuales
docker-compose run --rm shell dvc metrics show

# Comparar con versión anterior
docker-compose run --rm shell dvc metrics diff

# Ver plots
docker-compose run --rm shell dvc plots show
```

## 🐛 Troubleshooting

### Error: "DVC remote not configured"

```bash
# Verificar que .env tiene DVC_REMOTE_URL
cat .env | grep DVC_REMOTE

# Re-configurar dentro del contenedor
docker-compose run --rm shell bash scripts/dvc_docker_setup.sh
```

### Error: "AWS credentials not found"

```bash
# Verificar variables de entorno
docker-compose run --rm shell bash -c 'echo $AWS_ACCESS_KEY_ID'

# Re-crear .env con credenciales correctas
cp config/docker.env.template .env
# Editar .env
```

### Pipeline falla en alguna etapa

```bash
# Ver logs detallados
docker-compose run --rm shell dvc repro --verbose

# Ejecutar etapa específica
docker-compose run --rm shell dvc repro train --force

# Limpiar cache y re-ejecutar
docker-compose run --rm shell bash -c "dvc remove *.dvc && dvc repro"
```

### Contenedor no inicia

```bash
# Re-construir imagen
docker-compose build --no-cache

# Ver logs
docker-compose logs dvc-pipeline

# Verificar volumenes
docker volume ls
```

## 📚 Referencias

- [DVC Documentation](https://dvc.org/doc)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)

## 🤝 Equipo

**Equipo 52 - MLOps Project**
- Clasificación de Niveles de Obesidad
- Fase 2: Orquestación con DVC y Docker
