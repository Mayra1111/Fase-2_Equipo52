# 📚 Índice Maestro de Documentación

Guía completa para navegar toda la documentación del proyecto.

## 🎯 Para Empezar (Usuarios Nuevos)

Si es tu primera vez con el proyecto, sigue este orden:

1. **[README.md](README.md)** - ⭐ EMPIEZA AQUÍ
   - Visión general del proyecto
   - Características principales
   - Inicio rápido en 4 pasos
   - Comandos básicos

2. **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - ✅ Verificación
   - Pre-requisitos del sistema
   - Configuración paso a paso
   - Checklist de verificación completo
   - Troubleshooting básico

3. **[DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md)** - 📖 Guía Completa
   - Arquitectura del sistema
   - Configuración detallada
   - Todos los servicios explicados
   - Flujo de trabajo típico

## 📋 Por Tipo de Contenido

### 🚀 Guías de Uso

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| [README.md](README.md) | Guía principal | Primera lectura |
| [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) | Guía completa Docker + DVC | Uso diario |

### ⚙️ Configuración

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| [config/params.yaml](config/params.yaml) | Parámetros del pipeline | Ajustar experimentos |
| [config/dvc_config.yaml](config/dvc_config.yaml) | Configuración DVC | Setup de remote storage |
| [.env.example](.env.example) | Template variables de entorno | Crear archivo .env |

### 🏗️ Arquitectura y Diseño

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Diagramas y arquitectura completa | Entender el sistema |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen de implementación | Ver qué se hizo |

### 📝 Referencia

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| [FAQ.md](FAQ.md) | Preguntas frecuentes | Resolver dudas |
| [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) | Checklist de verificación | Validar setup |

### 🔧 Scripts Activos

| Script | Descripción | Uso |
|--------|-------------|-----|
| [scripts/run_eda.py](scripts/run_eda.py) | Análisis exploratorio | Pipeline DVC |
| [scripts/run_preprocess.py](scripts/run_preprocess.py) | Preprocesamiento | Pipeline DVC |
| [scripts/run_ml.py](scripts/run_ml.py) | Entrenamiento | Pipeline DVC |
| [scripts/run_evaluate.py](scripts/run_evaluate.py) | Evaluación | Pipeline DVC |
| [scripts/generate_visualizations.py](scripts/generate_visualizations.py) | Visualizaciones | Pipeline DVC |
| [scripts/dvc_push_manual.sh](scripts/dvc_push_manual.sh) | Push a S3 | Docker Compose |
| [scripts/dvc_pull_manual.sh](scripts/dvc_pull_manual.sh) | Pull desde S3 | Docker Compose |
| [scripts/dvc_run_and_push.sh](scripts/dvc_run_and_push.sh) | Pipeline + Push | Docker Compose |
| [scripts/dvc_repro_and_push.sh](scripts/dvc_repro_and_push.sh) | Repro + Push | Docker Compose |

### 📊 Configuración del Pipeline

| Archivo | Descripción | Propósito |
|---------|-------------|-----------|
| [dvc.yaml](dvc.yaml) | Definición del pipeline DVC | Pipeline principal |
| [dvc.lock](dvc.lock) | Lock file de DVC | Reproducibilidad |
| [docker-compose.yml](docker-compose.yml) | Orquestación Docker | Servicios |
| [Dockerfile](Dockerfile) | Imagen Docker | Container |

## 🎓 Rutas de Aprendizaje

### 🌱 Principiante (Nunca he usado el proyecto)

```
1. README.md (sección "Inicio Rápido")
   ↓
2. SETUP_CHECKLIST.md (completar checklist)
   ↓
3. DOCKER_DVC_GUIDE.md (leer "Servicios Disponibles")
   ↓
4. Ejecutar: docker-compose up dvc-pipeline
   ↓
5. Ver resultados en reports/
```

### 🌿 Intermedio (Ya ejecuté el pipeline una vez)

```
1. ARCHITECTURE.md (entender arquitectura)
   ↓
2. config/params.yaml (aprender configuración)
   ↓
3. FAQ.md (leer secciones relevantes)
   ↓
4. Experimentar con parámetros
   ↓
5. Ver resultados en MLflow
```

### 🌳 Avanzado (Voy a modificar el pipeline)

```
1. ARCHITECTURE.md (arquitectura completa)
   ↓
2. dvc.yaml (estudiar pipeline)
   ↓
3. src/ (código fuente)
   ↓
4. Modificar scripts en pipelines/
   ↓
5. Desarrollar nuevas features
```

## 🔍 Por Tarea Específica

### ¿Quieres hacer...?

#### 🚀 Ejecutar el pipeline por primera vez
1. [README.md](README.md) - Sección "Inicio Rápido"
2. [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
3. `docker-compose up dvc-pipeline`

#### ⚙️ Configurar credenciales de AWS/Cloud
1. [.env.example](.env.example) - Copiar a .env
2. [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) - Sección "Configuración de Remote Storage"
3. [FAQ.md](FAQ.md) - "¿Cómo obtengo las credenciales de AWS S3?"

#### 🔧 Modificar parámetros del modelo
1. [config/params.yaml](config/params.yaml) - Editar parámetros
2. [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) - Sección "Configuración"
3. `docker-compose up dvc-pipeline` - Re-ejecutar

#### 📊 Ver resultados y métricas
1. [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) - Sección "Monitoreo y Visualización"
2. `docker-compose up -d mlflow` - Iniciar MLflow UI
3. [FAQ.md](FAQ.md) - Sección "MLflow y Tracking"

#### 🐛 Resolver un problema
1. [FAQ.md](FAQ.md) - Sección "Troubleshooting"
2. [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Sección "Troubleshooting"
3. `docker-compose logs` - Ver logs

#### 🔄 Versionar datos/modelos
1. [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) - Sección "Versionado de Datos con DVC"
2. `docker-compose up dvc-push` - Push a S3
3. [FAQ.md](FAQ.md) - Sección "DVC y Versionado"

#### 🏗️ Entender la arquitectura
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Completo
2. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Detalles
3. [dvc.yaml](dvc.yaml) - Definición pipeline

#### 👥 Colaborar con el equipo
1. [FAQ.md](FAQ.md) - "¿Cómo colaboro con mi equipo?"
2. `docker-compose up dvc-pull` - Pull cambios
3. [DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md) - Sección "Flujo de Trabajo Típico"

#### 🧪 Ejecutar tests
1. [README.md](README.md) - Sección "Testing"
2. `docker-compose up test`
3. `pytest tests/` - Ejecutar manualmente

## 📖 Documentación por Categoría

### 📘 Documentación de Usuario

- **[README.md](README.md)** - Manual del usuario principal
- **[DOCKER_DVC_GUIDE.md](DOCKER_DVC_GUIDE.md)** - Guía de operación completa
- **[FAQ.md](FAQ.md)** - Preguntas frecuentes
- **[FAQ.md](FAQ.md)** - Preguntas y respuestas

### 🔧 Documentación Técnica

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Diseño del sistema
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Detalles de implementación

### ✅ Documentación de Proceso

- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Proceso de setup

### 📝 Archivos de Configuración

- **[config/params.yaml](config/params.yaml)** - Parámetros
- **[config/dvc_config.yaml](config/dvc_config.yaml)** - DVC
- **[.env.example](.env.example)** - Env vars
- **[dvc.yaml](dvc.yaml)** - Pipeline
- **[docker-compose.yml](docker-compose.yml)** - Servicios

## 🎯 Casos de Uso Comunes

### Caso 1: "Soy nuevo y quiero ejecutar el proyecto"

```
┌─────────────────────┐
│ docker-compose up   │ ← Ejecuta esto primero
│   dvc-pipeline      │
└──────────┬──────────┘
           │
           ├─ Lee README.md (Inicio Rápido)
           │
           ├─ Sigue SETUP_CHECKLIST.md
           │
           └─ Consulta FAQ.md si hay problemas
```

### Caso 2: "Quiero modificar los hiperparámetros"

```
┌─────────────────────┐
│ config/params.yaml  │ ← Edita este archivo
└──────────┬──────────┘
           │
           ├─ Lee DOCKER_DVC_GUIDE.md (Configuración)
           │
           ├─ Ejecuta: docker-compose up dvc-pipeline
           │
           └─ Ve resultados en reports/
```

### Caso 3: "Tengo un error y no sé qué hacer"

```
┌─────────────────────┐
│     FAQ.md          │ ← Busca tu error aquí
└──────────┬──────────┘
           │
           ├─ Si no está: SETUP_CHECKLIST.md (Troubleshooting)
           │
           ├─ Si persiste: docker-compose logs dvc-pipeline
           │
           └─ Último recurso: Crea un issue en GitHub
```

### Caso 4: "Quiero entender cómo funciona todo"

```
┌─────────────────────┐
│  ARCHITECTURE.md    │ ← Empieza aquí
└──────────┬──────────┘
           │
           ├─ Lee IMPLEMENTATION_SUMMARY.md
           │
           ├─ Estudia dvc.yaml
           │
           └─ Explora src/
```

## 🔗 Enlaces Rápidos

### Documentos Principales
- [📘 README](README.md)
- [🐳 DOCKER_DVC_GUIDE](DOCKER_DVC_GUIDE.md)
- [❓ FAQ](FAQ.md)
- [✅ SETUP_CHECKLIST](SETUP_CHECKLIST.md)

### Configuración
- [⚙️ params.yaml](config/params.yaml)
- [📝 .env.example](.env.example)
- [🔄 dvc.yaml](dvc.yaml)
- [🐳 docker-compose.yml](docker-compose.yml)

### Arquitectura
- [🏗️ ARCHITECTURE](ARCHITECTURE.md)
- [📋 IMPLEMENTATION_SUMMARY](IMPLEMENTATION_SUMMARY.md)

## 📞 Soporte

Si no encuentras lo que buscas:

1. ✅ Usa el buscador de tu editor (Ctrl+F) en [FAQ.md](FAQ.md)
2. 📖 Revisa la sección de troubleshooting en [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
3.  Busca en issues de GitHub del proyecto
4. 👥 Pregunta a tu equipo
5. 🆕 Crea un nuevo issue con tu pregunta

## 🎓 Glosario de Términos

- **DVC**: Data Version Control - Sistema de versionado de datos
- **Pipeline**: Secuencia de etapas de procesamiento
- **Stage**: Una etapa individual del pipeline
- **Remote**: Almacenamiento remoto para DVC (S3, GCS, etc.)
- **MLflow**: Sistema de tracking de experimentos ML
- **Docker Compose**: Herramienta para orquestar múltiples contenedores
- **Artifact**: Archivo generado (modelo, gráfico, métrica)
- **Checkpoint**: Estado guardado del pipeline

## 📊 Estadísticas de Documentación

```
Total de documentos: 7
Líneas de documentación: ~3000+
Diagramas: 8+
Scripts activos: 9
Archivos de configuración: 5
```

## 🎉 Feedback

¿Falta documentación de algo? ¿Algo no está claro?

1. Crea un issue en GitHub
2. Etiquétalo como "documentation"
3. El equipo lo revisará y actualizará

---

**Última actualización**: 2025
**Versión de documentación**: 2.1
**Equipo**: 52 - MLOps Project
