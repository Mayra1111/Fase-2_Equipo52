# 🔌 Modular FastAPI Service - Obesity Classification

Production-grade FastAPI application with maximum extensibility through modular router architecture.

---

## 📊 Architecture Overview

```
src/api/
├── main.py                      ← Lightweight orchestrator (90 lines)
├── config.py                    ← Centralized configuration
├── schemas.py                   ← Pydantic data models
├── dependencies.py              ← Model loading & dependency injection
├── routers/
│   ├── __init__.py             ← Router exports
│   ├── health.py               ← Health check endpoints (80 lines)
│   ├── prediction.py           ← Prediction endpoints (230 lines)
│   └── model_info.py           ← Model metadata endpoints (185 lines)
└── README.md                    ← This file
```

---

## 🎯 Design Philosophy

### Modular Architecture Benefits

✅ **Independent Extension**: Add new endpoints without modifying existing code
✅ **Clear Separation**: Each router handles specific domain
✅ **Easy Testing**: Test individual routers in isolation
✅ **Code Reusability**: Share schemas, config, and dependencies across routers
✅ **Maintainability**: Smaller, focused files are easier to understand
✅ **Scalability**: Easy to split routers into separate services later

### Layer Breakdown

| Layer | File | Responsibility |
|-------|------|-----------------|
| **Orchestrator** | main.py | App initialization, router registration, middleware |
| **Configuration** | config.py | Settings, environment variables, defaults |
| **Dependencies** | dependencies.py | Model loading, dependency injection, singletons |
| **Data Models** | schemas.py | Pydantic models, request/response validation |
| **Endpoints** | routers/*.py | Route definitions, business logic |

---

## 🚀 Endpoints

### Health & Info Routers (src/api/routers/health.py)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| **GET** | `/` | API information | None |
| **GET** | `/health` | Health check | None |
| **GET** | `/status` | Extended status | None |

### Prediction Router (src/api/routers/prediction.py)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| **POST** | `/predict` | Single prediction | None |
| **POST** | `/predict/batch` | Batch predictions | None |

### Model Info Router (src/api/routers/model_info.py)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| **GET** | `/model/info` | Model metadata | None |
| **GET** | `/model/features` | Feature requirements | None |
| **GET** | `/model/classes` | Prediction classes | None |

---

## 💻 Quick Start

### 1. Start the API

```bash
# Using uvicorn directly
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Using Python main
python src/api/main.py

# Using Docker
docker-compose up api
```

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 3. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
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

# Model info
curl http://localhost:8000/model/info

# Batch prediction
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [
      {/* sample 1 */},
      {/* sample 2 */}
    ]
  }'
```

---

## 🏗️ How to Extend

### Add a New Router

1. **Create new file** in `src/api/routers/`

```python
# src/api/routers/analytics.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/usage")
async def get_usage():
    """Get API usage statistics"""
    return {"total_predictions": 1000}
```

2. **Export in** `src/api/routers/__init__.py`

```python
from .analytics import router as analytics_router

__all__ = [
    "health_router",
    "prediction_router",
    "model_info_router",
    "analytics_router",  # ← Add new router
]
```

3. **Include in** `src/api/main.py`

```python
from src.api.routers import (
    health_router,
    prediction_router,
    model_info_router,
    analytics_router  # ← Import
)

# Include router
app.include_router(analytics_router)
```

### Add a New Endpoint to Existing Router

```python
# In src/api/routers/prediction.py
@router.get("/predict/explain/{prediction_id}")
async def explain_prediction(prediction_id: str):
    """Explain a previous prediction"""
    return {"explanation": "..."}
```

### Add New Configuration

```python
# In src/api/config.py
class Settings(BaseSettings):
    # Add new setting
    max_batch_size: int = Field(1000, description="Max samples in batch")

# Use in routers
from src.api.config import settings

@router.post("/predict/batch")
async def predict_batch(request: PredictionBatchRequest):
    if len(request.samples) > settings.max_batch_size:
        raise HTTPException(status_code=413, detail="Batch too large")
```

---

## 🔧 Configuration

### Environment Variables

All settings can be overridden via environment variables:

```bash
# .env file or export
API_VERSION=2.0.0
MODEL_VERSION=2.0.0
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### Update Configuration Centrally

```python
# src/api/config.py
class Settings(BaseSettings):
    app_name: str = "My Custom API Name"
    # All routers automatically use updated settings
```

---

## 🧪 Testing

### Test Individual Router

```python
# tests/test_prediction_router.py
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_single_prediction():
    response = client.post("/predict", json={
        "Age": 25.0,
        "Height": 1.75,
        # ... other fields
    })
    assert response.status_code == 200
    assert "prediction" in response.json()
```

### Test Dependency Injection

```python
# tests/test_dependencies.py
from src.api.dependencies import get_model_loader

def test_model_loader():
    loader = get_model_loader()
    assert loader.model_loaded
    assert loader.model is not None
```

### Run Tests

```bash
pytest tests/ -v --cov=src/api
```

---

## 📊 File Structure Comparison

### Before (Consolidated - 366 lines)

```
src/api/
├── main.py           (366 lines) - Everything in one file
├── schemas.py        (138 lines)
└── __init__.py
```

**Problems:**
- Hard to extend (modify main.py for new endpoints)
- Mixed concerns (routing, validation, config, logic)
- Harder to test (dependencies on global state)

### After (Modular - 529 lines across multiple files)

```
src/api/
├── main.py           (90 lines)  - Only orchestration
├── config.py         (58 lines)  - Configuration
├── dependencies.py   (168 lines) - Model loading
├── schemas.py        (138 lines) - Data models
├── routers/
│   ├── __init__.py   (12 lines)
│   ├── health.py     (80 lines)  - Health endpoints
│   ├── prediction.py (230 lines) - Prediction endpoints
│   └── model_info.py (185 lines) - Model info endpoints
└── README.md         - Documentation
```

**Benefits:**
- Easy to extend (add new file in routers/)
- Separated concerns (each layer has clear responsibility)
- Easier to test (dependency injection, singletons)
- Better documentation (docstrings on each router)

---

## 🔐 Security Considerations

### Current Implementation
- ✅ CORS configured
- ✅ Request validation (Pydantic)
- ✅ Error handling (no stack traces to client)
- ✅ Logging (track all requests)
- ❌ No API key authentication
- ❌ No rate limiting
- ❌ No HTTPS enforcement

### To Add Authentication

```python
# src/api/dependencies.py
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# In routers
@router.post("/predict", dependencies=[Depends(verify_api_key)])
async def predict_single(features: ObesityFeatures):
    # ...
```

### To Add Rate Limiting

```bash
pip install slowapi

# In main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# In routers
@router.get("/health", dependencies=[Depends(limiter.limit("100/minute"))])
async def health_check():
    # ...
```

---

## 📈 Performance Optimization

### Model Caching

✅ Implemented via `ModelLoader` singleton in dependencies.py

```python
# Model loaded once and reused across all requests
loader = get_model_loader()  # Always returns same instance
```

### Batch Processing

Implemented in `predict_batch` endpoint for bulk predictions

```python
# Single prediction: 1 request = 1 prediction
# Batch: 1 request = 100+ predictions (more efficient)
```

### Async Operations

All endpoints are async-ready for concurrent request handling

```python
async def predict_single(...):
    # Can handle multiple requests concurrently
```

---

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
  ports:
    - "8000:8000"
  volumes:
    - ./models:/app/models
  environment:
    - PYTHONUNBUFFERED=1
    - LOG_LEVEL=INFO
  command: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Production Considerations

- Use Gunicorn for multiple workers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app`
- Add reverse proxy (Nginx) for HTTPS
- Monitor logs and metrics
- Set up health checks for load balancers
- Use environment variables for sensitive config

---

## 📚 Code Quality

### Documentation

- ✅ Module-level docstrings
- ✅ Function docstrings with examples
- ✅ Type hints throughout
- ✅ Inline comments for complex logic

### Testing

- ✅ Unit tests for routers
- ✅ Integration tests with TestClient
- ✅ Dependency mocking
- ✅ Error case coverage

### Linting

```bash
# Format code
black src/api/

# Check types
mypy src/api/

# Lint
pylint src/api/

# Sort imports
isort src/api/
```

---

## 🔄 Migration from Consolidated API

If you started with the consolidated `main.py` and want to migrate to this modular structure:

1. **Keep schemas.py as is** - no changes needed
2. **Create config.py** - extract constants and settings
3. **Create dependencies.py** - extract model loading logic
4. **Create routers/** - split endpoints by domain
5. **Refactor main.py** - become lightweight orchestrator
6. **Update tests** - test routers independently

---

## 📞 Support

### Common Questions

**Q: How do I add authentication?**
A: See Security Considerations section

**Q: How do I add a new endpoint?**
A: See How to Extend section

**Q: How do I change the API port?**
A: Set `PORT=9000` environment variable or edit config.py

**Q: How do I enable HTTPS?**
A: Use reverse proxy (Nginx) or deploy with SSL certificate

---

## 📝 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Best Practices](https://fastapi.tiangolo.com/deployment/concepts/)
- [Testing Guide](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

---

**Version:** 2.0.0 (Modular)
**Status:** ✅ Production Ready
**Last Updated:** 2025-11-17
**Architecture:** Modular Router-Based
**Extensibility:** Maximum
