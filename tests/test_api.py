"""
Tests para el API de Inferencia

Tests completos para todos los endpoints del API usando pytest y httpx.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
def sample_input():
    """Fixture con datos de ejemplo para predicción"""
    return {
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
    }


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test del endpoint raíz"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test del endpoint de health check"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_readiness_endpoint():
    """Test del endpoint de readiness check"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]
        assert "model_loaded" in data


@pytest.mark.asyncio
async def test_predict_endpoint(sample_input):
    """Test del endpoint de predicción"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/predict", json=sample_input)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "prediction" in data
        assert "prediction_label" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert "bmi" in data
        assert "timestamp" in data
        assert "model_version" in data
        
        # Verificar tipos y rangos
        assert isinstance(data["prediction"], str)
        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
        assert isinstance(data["probabilities"], dict)
        assert isinstance(data["bmi"], float)


@pytest.mark.asyncio
async def test_predict_invalid_input():
    """Test de predicción con datos inválidos"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        invalid_data = {
            "Gender": "Invalid",  # Valor inválido
            "Age": 25.0,
            "Height": 1.75
            # Faltan campos requeridos
        }
        
        response = await client.post("/predict", json=invalid_data)
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_batch_predict_endpoint(sample_input):
    """Test del endpoint de predicción batch"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Crear batch con 3 inputs
        batch_data = [sample_input, sample_input, sample_input]
        
        response = await client.post("/predict/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que retorna lista
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verificar estructura de cada predicción
        for prediction in data:
            assert "prediction" in prediction
            assert "confidence" in prediction
            assert "bmi" in prediction


@pytest.mark.asyncio
async def test_model_info_endpoint():
    """Test del endpoint de información del modelo"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/model/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_name" in data
        assert "model_version" in data
        assert "model_framework" in data
        assert "classes" in data
        assert "features" in data


@pytest.mark.asyncio
async def test_model_version_endpoint():
    """Test del endpoint de versión del modelo"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/model/version")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_name" in data
        assert "model_version" in data
        assert "api_version" in data


@pytest.mark.asyncio
async def test_model_classes_endpoint():
    """Test del endpoint de clases del modelo"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/model/classes")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "classes" in data
        assert "total_classes" in data
        assert "descriptions" in data
        assert isinstance(data["classes"], list)


@pytest.mark.asyncio
async def test_model_features_endpoint():
    """Test del endpoint de features del modelo"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/model/features")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "features" in data
        assert "total_features" in data
        assert "descriptions" in data


@pytest.mark.asyncio
async def test_predict_bmi_calculation(sample_input):
    """Test de cálculo correcto del BMI"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/predict", json=sample_input)
        
        assert response.status_code == 200
        data = response.json()
        
        # Calcular BMI esperado
        expected_bmi = round(sample_input["Weight"] / (sample_input["Height"] ** 2), 2)
        assert data["bmi"] == expected_bmi


@pytest.mark.asyncio
async def test_predict_probabilities_sum():
    """Test que las probabilidades sumen aproximadamente 1"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sample_data = {
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
        
        response = await client.post("/predict", json=sample_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Sumar todas las probabilidades
        prob_sum = sum(data["probabilities"].values())
        assert abs(prob_sum - 1.0) < 0.01  # Tolerancia de 0.01


# Parametrized tests para diferentes inputs
@pytest.mark.parametrize("gender,expected_gender", [
    ("Male", "Male"),
    ("Female", "Female"),
])
@pytest.mark.asyncio
async def test_predict_different_genders(gender, expected_gender, sample_input):
    """Test con diferentes géneros"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sample_input["Gender"] = gender
        response = await client.post("/predict", json=sample_input)
        
        assert response.status_code == 200


@pytest.mark.parametrize("age", [15, 25, 45, 65, 90])
@pytest.mark.asyncio
async def test_predict_different_ages(age, sample_input):
    """Test con diferentes edades"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sample_input["Age"] = float(age)
        response = await client.post("/predict", json=sample_input)
        
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
