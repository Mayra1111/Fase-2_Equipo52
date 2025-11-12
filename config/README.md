# Configuración del Proyecto

Esta carpeta contiene todos los archivos de configuración centralizados del proyecto MLOps.

## Archivos

### params.yaml
Archivo principal de parámetros del proyecto. Contiene:
- Configuración de datos (rutas, split ratio)
- Parámetros de preprocesamiento
- Hiperparámetros de modelos
- Configuración de entrenamiento y evaluación
- Configuración de MLflow y DVC
- Configuración de reportes

Este archivo es utilizado por DVC para parametrizar el pipeline.

### dvc_config.yaml
Configuración específica de DVC:
- Definición de remotes (S3, GCS, local)
- Configuración de cache
- Políticas de tracking

### docker.env.template
Template para variables de entorno de Docker. Incluye:
- Credenciales de AWS
- URLs de remote storage
- Configuración de MLflow
- Variables de entorno del proyecto

**Importante**: Copiar este archivo a `.env` y completar con valores reales antes de usar Docker.

## Uso

Los archivos de configuración son referenciados por:
- **dvc.yaml**: Lee parámetros desde `config/params.yaml`
- **Docker**: Lee variables de entorno desde `.env` (basado en `docker.env.template`)
- **Scripts**: Pueden importar configuraciones desde estos archivos

## Ejemplo de uso en código Python

```python
import yaml
from pathlib import Path

# Cargar parámetros
with open('config/params.yaml', 'r') as f:
    params = yaml.safe_load(f)

# Acceder a parámetros
test_size = params['data']['test_size']
random_state = params['data']['random_state']
```

## Seguridad

- **NO** commitear archivos `.env` con credenciales reales
- Usar el template `docker.env.template` como referencia
- Las credenciales deben manejarse como secretos
