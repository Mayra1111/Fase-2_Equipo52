# Guía de Comandos Docker Compose

## 📋 Comandos Principales

### 1. `docker-compose up -d api`
**¿Qué hace?**
- Levanta el servicio API de FastAPI en **modo background (detached)**
- El API queda corriendo y escuchando en `http://localhost:8001`
- El flag `-d` significa "detached" (en segundo plano)

**Cuándo usarlo:**
- Cuando quieres que el API esté disponible para hacer predicciones
- Para probar el API con Postman o curl
- Para desarrollo continuo

**Ejemplo:**
```bash
# Levantar API
docker-compose up -d api

# Verificar que está corriendo
docker-compose ps

# Ver logs
docker-compose logs -f api

# Detener API
docker-compose stop api
# O
docker-compose down
```

**Acceder al API:**
- Documentación Swagger: http://localhost:8001/docs
- Health check: http://localhost:8001/health
- Predicción: POST http://localhost:8001/predict

---

### 2. `docker-compose up dvc-pipeline`
**¿Qué hace?**
- Ejecuta el **pipeline completo** orquestado por DVC
- Incluye: EDA → Preprocess → Train → Evaluate → Visualize
- Se ejecuta y **termina** (no queda corriendo)
- Es equivalente a: `docker-compose run --rm dvc-pipeline`

**Cuándo usarlo:**
- Para entrenar/re-entrenar el modelo
- Para ejecutar todo el pipeline desde cero
- Para reproducir experimentos

**Ejemplo:**
```bash
# Ejecutar pipeline completo
docker-compose up dvc-pipeline

# Ver logs mientras corre
docker-compose up dvc-pipeline  # (sin -d, verás los logs en tiempo real)
```

**¿Qué ejecuta?**
1. `dvc-pull` - Descarga datos de S3 (si está configurado)
2. `eda-pipeline` - Limpieza y análisis de datos
3. `ml-pipeline` - Entrenamiento de modelos
4. `evaluate` - Evaluación
5. `visualize` - Generación de visualizaciones

---

## 🔄 Diferencia entre `up` y `run`

### `docker-compose up`
- **Con `-d`**: Servicios quedan corriendo en background
- **Sin `-d`**: Servicios corren y muestras logs (Ctrl+C para detener)
- **Útil para**: Servicios que deben quedarse corriendo (API, MLflow)

### `docker-compose run --rm`
- Ejecuta un servicio **una vez** y luego lo elimina
- **Útil para**: Scripts que se ejecutan y terminan (tests, pipelines)

**Ejemplos:**
```bash
# Servicio que queda corriendo
docker-compose up -d api          # API queda activo
docker-compose up -d mlflow       # MLflow queda activo

# Servicio que se ejecuta y termina
docker-compose run --rm test      # Ejecuta tests y termina
docker-compose run --rm eda-pipeline  # Ejecuta EDA y termina
```

---

## 🎯 Flujo de Trabajo Recomendado

### Primera vez / Setup completo:
```bash
# 1. Construir imágenes
docker-compose build

# 2. Ejecutar pipeline completo (entrenar modelo)
docker-compose up dvc-pipeline

# 3. Levantar API para predicciones
docker-compose up -d api

# 4. (Opcional) Levantar MLflow para ver experimentos
docker-compose up -d mlflow
```

### Desarrollo diario:
```bash
# Ejecutar solo EDA
docker-compose run --rm eda-pipeline

# Ejecutar solo entrenamiento
docker-compose run --rm ml-pipeline

# Ejecutar tests
docker-compose run --rm test

# Ver logs del API
docker-compose logs -f api
```

### Detener servicios:
```bash
# Detener todos los servicios
docker-compose down

# Detener solo API
docker-compose stop api

# Detener y eliminar contenedores
docker-compose down --remove-orphans
```

---

## 📊 Servicios Disponibles

| Servicio | Comando | ¿Queda corriendo? | Puerto |
|----------|---------|-------------------|--------|
| API | `docker-compose up -d api` | ✅ Sí | 8001 |
| MLflow | `docker-compose up -d mlflow` | ✅ Sí | 5001 |
| Pipeline DVC | `docker-compose up dvc-pipeline` | ❌ No | - |
| Tests | `docker-compose run --rm test` | ❌ No | - |
| EDA | `docker-compose run --rm eda-pipeline` | ❌ No | - |
| ML Training | `docker-compose run --rm ml-pipeline` | ❌ No | - |
| Drift Detection | `docker-compose run --rm detect-drift` | ❌ No | - |

---

## ⚠️ Troubleshooting

### API no responde:
```bash
# Verificar que está corriendo
docker-compose ps

# Ver logs
docker-compose logs api

# Reiniciar
docker-compose restart api
```

### Pipeline falla:
```bash
# Ver logs detallados
docker-compose up dvc-pipeline  # (sin -d para ver logs)

# Reconstruir imágenes
docker-compose build --no-cache

# Verificar datos
docker-compose run --rm shell
# Dentro del shell: ls -la data/interim/
```

### Limpiar todo:
```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar también imágenes
docker-compose down --rmi all

# Limpiar volúmenes (CUIDADO: borra datos)
docker-compose down -v
```

