# 🚀 API de Inferencia - Clasificación de Obesidad

API REST construida con FastAPI para realizar predicciones en tiempo real usando el modelo de clasificación de obesidad entrenado.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Inicio Rápido](#inicio-rápido)
- [Endpoints](#endpoints)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Schema de Datos](#schema-de-datos)
- [Versionado del Modelo](#versionado-del-modelo)
- [Testing](#testing)
- [Despliegue](#despliegue)

## ✨ Características

- ✅ **Validación automática** de entrada con Pydantic
- ✅ **Documentación interactiva** con Swagger/OpenAPI
- ✅ **Health checks** para monitoreo
- ✅ **Predicciones individuales y por lote**
- ✅ **Información del modelo** (versión, clases, features)
- ✅ **Manejo de errores** robusto
- ✅ **Portabilidad** con Docker
- ✅ **Seguridad** (volumen read-only para modelos)

## 🚀 Inicio Rápido

### 1. Levantar el servicio

```bash
# Con Docker Compose (recomendado)
docker-compose up api

# Acceder a la documentación interactiva
http://localhost:8000/docs
```

### 2. Verificar que el servicio esté activo

```bash
curl http://localhost:8000/health
```

## 📌 Endpoints

### Health & Status

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información general del API |
| `/health` | GET | Health check básico |
| `/ready` | GET | Readiness check (modelo cargado) |

### Predicción

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/predict` | POST | Predicción individual |
| `/predict/batch` | POST | Predicción por lote |

### Información del Modelo

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/model/info` | GET | Información completa del modelo |
| `/model/version` | GET | Versión del modelo y API |
| `/model/classes` | GET | Clases que predice el modelo |
| `/model/features` | GET | Features que espera el modelo |

## 💡 Ejemplos de Uso

### Predicción Individual

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Gender": "Male",
    "Age": 25.0,
    "Height": 1.75,
    "Weight": 85.0,
    "family_history_with_overweight": "yes",
    "FAVC": "yes",
    "FCVC": 3.0,
    "NCP": 3.0,
    "CAEC": "Sometimes",
    "SMOKE": "no",
    "CH2O": 2.0,
    "SCC": "no",
    "FAF": 2.0,
    "TUE": 1.0,
    "CALC": "Sometimes",
    "MTRANS": "Public_Transportation"
  }'
```

**Respuesta:**

```json
{
  "prediction": "Obesity_Type_I",
  "prediction_label": "Obesidad Tipo I",
  "confidence": 0.92,
  "probabilities": {
    "Insufficient_Weight": 0.01,
    "Normal_Weight": 0.02,
    "Overweight_Level_I": 0.03,
    "Overweight_Level_II": 0.02,
    "Obesity_Type_I": 0.92,
    "Obesity_Type_II": 0.00,
    "Obesity_Type_III": 0.00
  },
  "bmi": 27.76,
  "timestamp": "2025-11-12T10:30:00",
  "model_version": "v1.0"
}
```

### Predicción por Lote

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '[
    { "Gender": "Male", "Age": 25, ... },
    { "Gender": "Female", "Age": 30, ... },
    { "Gender": "Male", "Age": 45, ... }
  ]'
```

### Información del Modelo

```bash
# Versión del modelo
curl http://localhost:8000/model/version

# Clases que predice
curl http://localhost:8000/model/classes

# Features esperadas
curl http://localhost:8000/model/features
```

### Python Client Example

```python
import requests

url = "http://localhost:8000/predict"

data = {
    "Gender": "Female",
    "Age": 30.0,
    "Height": 1.65,
    "Weight": 70.0,
    "family_history_with_overweight": "no",
    "FAVC": "no",
    "FCVC": 2.0,
    "NCP": 3.0,
    "CAEC": "Sometimes",
    "SMOKE": "no",
    "CH2O": 2.0,
    "SCC": "yes",
    "FAF": 3.0,
    "TUE": 1.0,
    "CALC": "no",
    "MTRANS": "Walking"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Predicción: {result['prediction_label']}")
print(f"Confianza: {result['confidence']:.2%}")
print(f"BMI: {result['bmi']}")
```

## 📊 Schema de Datos

### Input Schema (ObesityInput)

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| Gender | string | Male/Female | Género |
| Age | float | 10-100 | Edad en años |
| Height | float | 1.0-2.5 | Altura en metros |
| Weight | float | 30-200 | Peso en kilogramos |
| family_history_with_overweight | string | yes/no | Historial familiar |
| FAVC | string | yes/no | Consumo frecuente de alimentos calóricos |
| FCVC | float | 1-3 | Frecuencia consumo vegetales |
| NCP | float | 1-4 | Número de comidas principales |
| CAEC | string | no/Sometimes/Frequently/Always | Consumo entre comidas |
| SMOKE | string | yes/no | Fumador |
| CH2O | float | 1-3 | Consumo agua (litros/día) |
| SCC | string | yes/no | Monitorea calorías |
| FAF | float | 0-3 | Frecuencia actividad física (días/semana) |
| TUE | float | 0-2 | Tiempo uso dispositivos (horas) |
| CALC | string | no/Sometimes/Frequently/Always | Consumo alcohol |
| MTRANS | string | Automobile/Motorbike/Bike/Public_Transportation/Walking | Transporte |

### Output Schema (ObesityPrediction)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| prediction | string | Clase predicha |
| prediction_label | string | Etiqueta en español |
| confidence | float | Confianza (0-1) |
| probabilities | dict | Probabilidades por clase |
| bmi | float | BMI calculado |
| timestamp | datetime | Timestamp de la predicción |
| model_version | string | Versión del modelo usado |

### Clases de Obesidad

1. **Insufficient_Weight** - Peso Insuficiente
2. **Normal_Weight** - Peso Normal
3. **Overweight_Level_I** - Sobrepeso Nivel I
4. **Overweight_Level_II** - Sobrepeso Nivel II
5. **Obesity_Type_I** - Obesidad Tipo I
6. **Obesity_Type_II** - Obesidad Tipo II
7. **Obesity_Type_III** - Obesidad Tipo III

## 🏷️ Versionado del Modelo

### Información de Versionado

- **Modelo**: `obesity_classifier`
- **Versión**: `v1.0`
- **Framework**: `XGBoost + SMOTE`
- **Accuracy**: `97%` (en conjunto de validación)
- **Ubicación**: `models/best_pipeline.joblib`
- **Metadata**: `models/model_metadata.joblib`

### Tracking con DVC

El modelo está versionado con DVC y almacenado en S3:

```bash
# Ubicación en S3
s3://itesm-mna/202502-equipo52/dvc-storage/models/best_pipeline.joblib

# Fecha de entrenamiento
2025-11-12

# Pipeline que generó el modelo
dvc.yaml (stage: train)
```

### Actualizar Modelo

Para usar una nueva versión del modelo:

1. Entrenar nuevo modelo con el pipeline DVC
2. El modelo se guarda en `models/best_pipeline.joblib`
3. Reiniciar el servicio API:
   ```bash
   docker-compose restart api
   ```

## 🧪 Testing

### Ejecutar Tests

```bash
# Con pytest
pytest tests/test_api.py -v

# Con coverage
pytest tests/test_api.py --cov=api --cov-report=html

# Tests específicos
pytest tests/test_api.py::test_predict_endpoint -v
```

### Tests Incluidos

- ✅ Health checks
- ✅ Predicción individual
- ✅ Predicción por lote
- ✅ Validación de entrada
- ✅ Manejo de errores
- ✅ Información del modelo
- ✅ Cálculo de BMI
- ✅ Tests parametrizados

## 🚢 Despliegue

### Desarrollo

```bash
docker-compose up api
```

### Producción

```bash
# Build de imagen optimizada
docker build -f Dockerfile.api -t obesity-api:v1.0 .

# Run en producción
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  --name obesity-api \
  obesity-api:v1.0
```

### Variables de Entorno

```bash
MODEL_PATH=models/best_pipeline.joblib
METADATA_PATH=models/model_metadata.joblib
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔒 Seguridad

- ✅ Usuario no-root en container
- ✅ Volumen de modelos en modo read-only
- ✅ CORS configurado
- ✅ Validación de entrada con Pydantic
- ✅ Health checks para monitoring

## 📈 Performance

- **Tiempo de carga del modelo**: ~2-3 segundos
- **Tiempo de respuesta**: ~50-100ms por predicción
- **Throughput**: ~100 requests/segundo (single container)
- **Tamaño de imagen**: ~200MB (vs ~2GB del pipeline completo)

## 🤝 Soporte

Para problemas o preguntas:
1. Ver [FAQ.md](../FAQ.md)
2. Revisar logs: `docker-compose logs api`
3. Crear issue en GitHub

---

**Equipo 52 - MLOps Project**
**Versión API**: 1.0.0
**Última actualización**: 2025-11-12
