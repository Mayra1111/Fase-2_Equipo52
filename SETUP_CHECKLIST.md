# ✅ Checklist de Verificación - Configuración y Despliegue

Usa este checklist para verificar que todo está correctamente configurado antes de ejecutar el pipeline.

## 📋 Pre-requisitos

### Sistema
- [ ] Docker instalado y funcionando (`docker --version`)
- [ ] Docker Compose instalado (`docker-compose --version`)
- [ ] Git instalado y configurado (`git --version`)
- [ ] Al menos 4GB de RAM disponible
- [ ] Al menos 10GB de espacio en disco

### Credenciales (si usas cloud storage)
- [ ] Cuenta de AWS/GCS/Azure configurada
- [ ] Bucket/Container de storage creado
- [ ] Credenciales de acceso generadas
- [ ] Permisos de lectura/escritura verificados

## 🔧 Configuración Inicial

### Archivos de Configuración
- [ ] Archivo `.env` creado desde `config/docker.env.template`
- [ ] Variables `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` configuradas (si usas S3)
- [ ] Variable `DVC_REMOTE_URL` configurada con tu bucket
- [ ] Variable `DVC_REMOTE_NAME` definida (por defecto: `myremote`)
- [ ] Archivo `.env` en `.gitignore` (NO commitear credenciales)

### Verificación de Configuración
```bash
# Ejecutar estos comandos para verificar
cat .env | grep -v "^#" | grep -v "^$"  # Ver variables de entorno
docker-compose config                    # Validar docker-compose.yml
docker-compose run --rm shell env | grep DVC  # Ver variables DVC en container
```

### Estructura de Directorios
- [ ] Carpeta `data/raw/` existe con datos originales
- [ ] Carpeta `models/` existe
- [ ] Carpeta `reports/figures/` existe
- [ ] Carpeta `reports/metrics/` existe
- [ ] Carpeta `config/` con archivos de configuración

## 🐳 Docker

### Construcción de Imagen
```bash
# Construir imagen Docker
docker-compose build

# Verificaciones:
```
- [ ] Imagen construida sin errores
- [ ] DVC instalado en la imagen (`docker-compose run --rm shell dvc version`)
- [ ] Dependencias Python instaladas (`docker-compose run --rm shell pip list`)
- [ ] Scripts ejecutables (`docker-compose run --rm shell ls -la scripts/`)

### Servicios Docker
```bash
# Listar servicios disponibles
docker-compose config --services
```
- [ ] Servicio `dvc-pipeline` disponible
- [ ] Servicio `dvc-pull` disponible
- [ ] Servicio `dvc-push` disponible
- [ ] Servicio `mlflow` disponible
- [ ] Servicio `shell` disponible
- [ ] Servicio `test` disponible

## 🔄 DVC

### Configuración DVC
```bash
# Verificar configuración DVC
docker-compose run --rm shell bash scripts/dvc_docker_setup.sh
```
- [ ] DVC inicializado correctamente
- [ ] Remote storage configurado
- [ ] Credenciales reconocidas
- [ ] Conexión al remote exitosa

### Pipeline DVC
```bash
# Verificar pipeline
docker-compose run --rm shell dvc dag
```
- [ ] Archivo `dvc.yaml` válido
- [ ] 5 etapas definidas (eda, preprocess, train, evaluate, visualize)
- [ ] Dependencias correctas entre etapas
- [ ] Parámetros enlazados desde `config/params.yaml`

### Primera Ejecución de Prueba
```bash
# Probar una etapa simple
docker-compose run --rm shell dvc repro eda --dry
```
- [ ] Comando ejecuta sin errores
- [ ] Muestra las etapas que se ejecutarían
- [ ] Archivos de entrada existen

## 📊 MLflow

### Servidor MLflow
```bash
# Iniciar MLflow UI
docker-compose up -d mlflow
```
- [ ] Servicio inicia sin errores
- [ ] Puerto 5001 accesible
- [ ] UI carga en navegador (http://localhost:5001)
- [ ] Carpeta `mlruns/` existe y tiene contenido

## 🧪 Tests

### Ejecución de Tests
```bash
# Ejecutar tests
docker-compose up test
```
- [ ] Tests ejecutan sin errores de sintaxis
- [ ] Cobertura de código generada
- [ ] Todos los tests críticos pasan

## 🚀 Primera Ejecución Completa

### Preparación
- [ ] Datos en `data/raw/` listos
- [ ] Configuración verificada
- [ ] Remote storage accesible (si aplica)
- [ ] Suficiente espacio en disco

### Ejecución Pipeline Completo
```bash
# Ejecutar pipeline completo
docker-compose up dvc-pipeline
```
Verificar durante la ejecución:
- [ ] Etapa `eda` completa exitosamente
- [ ] Etapa `preprocess` completa exitosamente
- [ ] Etapa `train` completa exitosamente
- [ ] Etapa `evaluate` completa exitosamente
- [ ] Etapa `visualize` completa exitosamente

### Verificación de Outputs
```bash
# Verificar outputs generados
docker-compose run --rm shell bash -c "
  ls -la data/interim/
  ls -la models/
  ls -la reports/figures/
  ls -la reports/metrics/
"
```
- [ ] `data/interim/dataset_limpio_refactored.csv` existe
- [ ] `models/best_pipeline.joblib` existe
- [ ] `models/model_metadata.joblib` existe
- [ ] Figuras generadas en `reports/figures/`
- [ ] Métricas generadas en `reports/metrics/`

### Verificación de Métricas
```bash
# Ver métricas
docker-compose run --rm shell dvc metrics show
```
- [ ] Métricas de EDA disponibles
- [ ] Métricas de modelo disponibles
- [ ] Métricas de evaluación disponibles
- [ ] Valores de métricas razonables (accuracy > 0.5, etc.)

## 🔒 Versionado

### Push a Remote Storage
```bash
# Subir datos/modelos
docker-compose up dvc-push
```
- [ ] Comando ejecuta sin errores
- [ ] Datos subidos al remote storage
- [ ] Modelos subidos al remote storage
- [ ] Verificar en consola del cloud provider

### Commit a Git
```bash
# Commit archivos .dvc
git add .
git status
```
- [ ] Archivos `.dvc` listados para commit
- [ ] Archivo `.dvc/config` incluido
- [ ] Archivos grandes NO en staging (están en .gitignore)
- [ ] Archivo `.env` NO en staging

## 🔧 Troubleshooting

Si algo falla, verificar:

### Errores de Docker
- [ ] Docker daemon está corriendo
- [ ] Permisos adecuados para usuario
- [ ] Suficiente memoria asignada a Docker
- [ ] Volúmenes montados correctamente

### Errores de DVC
- [ ] Variables de entorno correctas
- [ ] Remote storage accesible
- [ ] Credenciales válidas
- [ ] Archivos de datos existen

### Errores de Python
- [ ] Todas las dependencias instaladas
- [ ] Versión de Python correcta (3.10)
- [ ] PYTHONPATH configurado correctamente
- [ ] Imports funcionan correctamente

### Comandos de Diagnóstico
```bash
# Ver logs detallados
docker-compose logs dvc-pipeline

# Verificar estado de DVC
docker-compose run --rm shell dvc status

# Verificar configuración
docker-compose run --rm shell dvc config list

# Verificar remote
docker-compose run --rm shell dvc remote list -v

# Entrar al shell para debugging
docker-compose run --rm shell
```

## ✅ Checklist Final

Antes de considerar la configuración completa:
- [ ] Pipeline completo ejecutado exitosamente al menos una vez
- [ ] MLflow UI accesible y mostrando experimentos
- [ ] Versionado DVC funcionando (push/pull)
- [ ] Tests pasando
- [ ] Métricas generadas y razonables
- [ ] Documentación leída y entendida
- [ ] Equipo capacitado en el uso del sistema

## 📝 Notas

Fecha de verificación: _______________

Persona que verificó: _______________

Problemas encontrados:
___________________________________
___________________________________
___________________________________

Resoluciones aplicadas:
___________________________________
___________________________________
___________________________________

## 🎉 Confirmación

Una vez completado todo el checklist:

```bash
# Crear tag de confirmación
git tag -a setup-verified-$(date +%Y%m%d) -m "Setup verified and working"
git push --tags

# Documentar en archivo
echo "Setup verified on $(date)" >> SETUP_STATUS.txt
echo "Verified by: $USER" >> SETUP_STATUS.txt
git add SETUP_STATUS.txt
git commit -m "Setup verification completed"
git push
```

---

**¡Sistema listo para producción!** 🚀

Para comenzar a trabajar, consulta:
- `README.md` - Documentación general
- `DOCKER_DVC_GUIDE.md` - Guía de uso
- `EXAMPLES.md` - Ejemplos prácticos
