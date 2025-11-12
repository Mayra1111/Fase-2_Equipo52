# ❓ Preguntas Frecuentes (FAQ)

## 📋 Índice

1. [Configuración Inicial](#configuración-inicial)
2. [DVC y Versionado](#dvc-y-versionado)
3. [Docker y Contenedores](#docker-y-contenedores)
4. [Pipeline y Ejecución](#pipeline-y-ejecución)
5. [MLflow y Tracking](#mlflow-y-tracking)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Configuración Inicial

### ❓ ¿Necesito instalar Python o DVC localmente?

**R:** No. Todo está containerizado con Docker. Solo necesitas:
- Docker
- Docker Compose
- Git
- Un editor de texto para el archivo `.env`

### ❓ ¿Cómo obtengo las credenciales de AWS S3?

**R:** 
1. Accede a la consola de AWS
2. IAM → Users → Security credentials
3. Create access key
4. Copia `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`
5. Pégalas en tu archivo `.env`

Permisos necesarios:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:*"],
    "Resource": [
      "arn:aws:s3:::tu-bucket/*",
      "arn:aws:s3:::tu-bucket"
    ]
  }]
}
```

### ❓ ¿Puedo usar almacenamiento local en lugar de S3?

**R:** Sí, para desarrollo. En tu `.env`:
```bash
DVC_REMOTE_URL=/tmp/dvc-storage
DVC_REMOTE_NAME=local
```

Luego crea el directorio:
```bash
mkdir -p /tmp/dvc-storage
```

### ❓ ¿Qué hacer si no tengo archivo .env?

**R:** Créalo desde el template:
```bash
cp config/docker.env.template .env
```
Luego edita `.env` con tus credenciales.

---

## DVC y Versionado

### ❓ ¿Qué diferencia hay entre DVC y Git?

**R:** 
- **Git**: Versiona código fuente (archivos pequeños, texto)
- **DVC**: Versiona datos y modelos (archivos grandes, binarios)

Git almacena archivos `.dvc` (pointers), DVC almacena los datos reales en remote storage.

### ❓ ¿Cómo funciona `dvc pull`?

**R:** 
1. Lee los archivos `.dvc` (pointers con hashes)
2. Conecta al remote storage
3. Descarga los archivos reales basándose en los hashes
4. Los coloca en las ubicaciones correctas

```bash
docker-compose up dvc-pull
```

### ❓ ¿Cuándo debo hacer `dvc push`?

**R:** Después de generar nuevos datos o modelos:
```bash
# Ejecutar pipeline
docker-compose up dvc-pipeline

# Subir resultados
docker-compose up dvc-push

# Commit archivos .dvc en Git
git add *.dvc
git commit -m "New model version"
git push
```

### ❓ ¿Puedo ver el historial de versiones?

**R:** Sí:
```bash
# Ver commits de Git
git log --oneline

# Checkout a versión anterior
git checkout <commit-hash>

# Pull datos de esa versión
docker-compose up dvc-pull
```

### ❓ ¿Qué archivos debo commitear en Git?

**R:** 
✅ Commitear:
- Código fuente (`src/`, `scripts/`)
- Configuración (`config/`, `dvc.yaml`)
- Archivos `.dvc` (pointers)
- Archivos `.dvc/config`
- Documentación

❌ NO commitear:
- Archivo `.env` (credenciales)
- Datos crudos (`data/`)
- Modelos (`models/`)
- Cache de DVC (`.dvc/cache/`)

---

## Docker y Contenedores

### ❓ ¿Cuánta RAM necesita Docker?

**R:** Mínimo 4GB, recomendado 8GB o más. Ajusta en Docker Desktop:
- Settings → Resources → Memory

### ❓ ¿Cómo veo los logs de un servicio?

**R:**
```bash
# Logs en tiempo real
docker-compose logs -f dvc-pipeline

# Últimas 100 líneas
docker-compose logs --tail=100 dvc-pipeline

# Todos los servicios
docker-compose logs
```

### ❓ ¿Cómo entro al contenedor para debugging?

**R:**
```bash
# Shell interactivo
docker-compose run --rm shell

# O conectar a contenedor en ejecución
docker-compose exec dvc-pipeline bash
```

### ❓ ¿Cómo limpio los contenedores y volúmenes?

**R:**
```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Limpiar todo (incluyendo imágenes)
docker-compose down --rmi all -v

# Rebuild desde cero
docker-compose build --no-cache
```

### ❓ El contenedor no inicia, ¿qué hago?

**R:** 
1. Ver logs:
   ```bash
   docker-compose logs dvc-pipeline
   ```

2. Verificar sintaxis:
   ```bash
   docker-compose config
   ```

3. Rebuild imagen:
   ```bash
   docker-compose build --no-cache
   ```

4. Verificar recursos disponibles (RAM, disco)

---

## Pipeline y Ejecución

### ❓ ¿Qué hace `dvc repro`?

**R:** Ejecuta el pipeline DVC:
1. Lee `dvc.yaml`
2. Compara hashes de dependencias
3. Ejecuta solo etapas que cambiaron
4. Genera outputs y métricas

Es inteligente: solo re-ejecuta lo necesario.

### ❓ ¿Cómo fuerzo la re-ejecución de una etapa?

**R:**
```bash
# Forzar etapa específica
docker-compose run --rm shell dvc repro train --force

# Forzar todo el pipeline
docker-compose run --rm shell dvc repro --force
```

### ❓ ¿Cómo ejecuto solo una etapa del pipeline?

**R:**
```bash
# Solo EDA
docker-compose run --rm shell dvc repro eda

# Solo entrenamiento
docker-compose run --rm shell dvc repro train

# Solo evaluación
docker-compose run --rm shell dvc repro evaluate
```

### ❓ ¿Cómo modifico los parámetros del pipeline?

**R:** Edita `config/params.yaml`:
```yaml
training:
  cv_folds: 10  # Cambiar de 5 a 10
  scoring: f1   # Cambiar de accuracy a f1
```

Luego:
```bash
docker-compose up dvc-pipeline
```

DVC automáticamente detecta el cambio y re-ejecuta las etapas afectadas.

### ❓ ¿Puedo ejecutar múltiples experimentos en paralelo?

**R:** Sí, pero cada uno necesita su propio directorio o branch:
```bash
# Experimento 1 en branch
git checkout -b experiment-1
# Modificar params
docker-compose up dvc-pipeline

# Experimento 2 en otro branch
git checkout -b experiment-2
# Modificar params
docker-compose up dvc-pipeline
```

### ❓ ¿Cómo veo el grafo del pipeline?

**R:**
```bash
# ASCII art
docker-compose run --rm shell dvc dag

# Generar imagen (requiere graphviz)
docker-compose run --rm shell dvc dag --dot | dot -Tpng -o pipeline.png
```

---

## MLflow y Tracking

### ❓ ¿Cómo accedo a MLflow UI?

**R:**
```bash
# Iniciar servidor
docker-compose up -d mlflow

# Acceder a http://localhost:5001
```

### ❓ No veo mis experimentos en MLflow, ¿por qué?

**R:** Verifica:
1. El directorio `mlruns/` existe
2. El pipeline ha ejecutado al menos una vez
3. MLflow está configurado en el código:
   ```python
   import mlflow
   mlflow.set_tracking_uri("./mlruns")
   mlflow.set_experiment("nombre_experimento")
   ```

### ❓ ¿Cómo comparo experimentos en MLflow?

**R:** En MLflow UI:
1. Selecciona experimentos (checkboxes)
2. Click en "Compare"
3. Visualiza métricas, parámetros y artefactos

### ❓ ¿Puedo usar MLflow remoto?

**R:** Sí, configura en `.env`:
```bash
MLFLOW_TRACKING_URI=http://tu-servidor-mlflow:5000
```

---

## Troubleshooting

### ❓ Error: "DVC remote not configured"

**R:** 
```bash
# Verificar .env
cat .env | grep DVC_REMOTE

# Re-configurar
docker-compose run --rm shell bash scripts/dvc_docker_setup.sh
```

### ❓ Error: "AWS credentials not found"

**R:** 
1. Verifica que `.env` tiene:
   ```
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   ```

2. Verifica que se cargan en el contenedor:
   ```bash
   docker-compose run --rm shell env | grep AWS
   ```

3. Test de conexión:
   ```bash
   docker-compose run --rm shell aws s3 ls s3://tu-bucket/
   ```

### ❓ Error: "Out of memory"

**R:** 
1. Aumenta memoria en Docker Desktop
2. Reduce `cv_folds` en `config/params.yaml`
3. Reduce tamaño del dataset para pruebas

### ❓ Error: "Permission denied" en scripts

**R:**
```bash
# Dar permisos de ejecución
chmod +x scripts/*.sh

# O dentro del contenedor
docker-compose run --rm shell chmod +x scripts/*.sh
```

### ❓ Pipeline falla pero no muestra error claro

**R:**
```bash
# Ver logs detallados
docker-compose run --rm shell dvc repro --verbose

# Ver logs de Python
docker-compose run --rm shell python scripts/run_ml.py --debug
```

### ❓ ¿Cómo reseteo todo y empiezo de nuevo?

**R:**
```bash
# CUIDADO: Esto borra todo

# 1. Detener contenedores
docker-compose down -v

# 2. Limpiar outputs
rm -rf data/interim/* data/processed/* models/* reports/*

# 3. Limpiar cache DVC
rm -rf .dvc/cache/*

# 4. Rebuild
docker-compose build --no-cache

# 5. Re-ejecutar
docker-compose up dvc-pipeline
```

---

## Best Practices

### ❓ ¿Cuál es el workflow recomendado?

**R:**
```bash
# 1. Pull de código y datos
git pull
docker-compose up dvc-pull

# 2. Hacer cambios
nano config/params.yaml

# 3. Probar en shell
docker-compose run --rm shell
> dvc repro --dry  # Ver qué se ejecutará
> exit

# 4. Ejecutar pipeline
docker-compose up dvc-pipeline

# 5. Verificar resultados
docker-compose run --rm shell dvc metrics show

# 6. Si todo OK, versionar
docker-compose up dvc-push
git add .
git commit -m "Descripción del cambio"
git push
```

### ❓ ¿Cómo organizo múltiples experimentos?

**R:**
1. Usa branches de Git:
   ```bash
   git checkout -b experiment-xgboost-tuning
   ```

2. Documenta en commits:
   ```bash
   git commit -m "Experiment: XGBoost with max_depth=10"
   ```

3. Usa tags para versiones importantes:
   ```bash
   git tag -a v1.0 -m "First production model"
   ```

### ❓ ¿Qué debo documentar?

**R:** 
- Cambios en parámetros y por qué
- Resultados de experimentos importantes
- Decisiones de diseño del modelo
- Problemas encontrados y soluciones

Usa:
- Commits descriptivos en Git
- Comentarios en `config/params.yaml`
- Notes en MLflow experiments
- Archivos Markdown en `docs/`

### ❓ ¿Cómo colaboro con mi equipo?

**R:**
1. **Código**: Usa pull requests en Git
2. **Datos**: Comparte via DVC remote
3. **Resultados**: Comparte MLflow tracking URI
4. **Documentación**: Mantén README actualizado

Workflow:
```bash
# Persona A
git checkout -b feature-x
# Hace cambios
docker-compose up dvc-pipeline
docker-compose up dvc-push
git push origin feature-x
# Crea Pull Request

# Persona B
git fetch origin
git checkout feature-x
docker-compose up dvc-pull
docker-compose up dvc-pipeline
# Revisa resultados
```

### ❓ ¿Con qué frecuencia debo hacer push a DVC?

**R:** 
- **Siempre**: Cuando el modelo mejora significativamente
- **Siempre**: Antes de merge a main/master
- **Opcional**: Para experimentos temporales
- **No necesario**: Para pruebas rápidas locales

### ❓ ¿Cómo manejo datos sensibles?

**R:**
1. NUNCA commitear credenciales en Git
2. Usar `.env` (en .gitignore)
3. Encriptar datos sensibles antes de DVC push
4. Usar secrets management (AWS Secrets Manager, etc.)
5. Anonimizar datos cuando sea posible

---

## 💡 Tips Rápidos

### Aliases Útiles

Agregar a `~/.bashrc` o `~/.zshrc`:
```bash
alias dvc-shell='docker-compose run --rm shell'
alias dvc-run='docker-compose up dvc-pipeline'
alias dvc-status='docker-compose run --rm shell dvc status'
alias mlflow-ui='docker-compose up -d mlflow && echo "http://localhost:5001"'
```

### Scripts de Ayuda

Ver estado rápido:
```bash
docker-compose run --rm shell bash -c "
  echo '=== DVC Status ==='
  dvc status
  echo -e '\n=== Métricas ==='
  dvc metrics show
  echo -e '\n=== Remotes ==='
  dvc remote list
"
```

---

## 📚 Recursos Adicionales

- [Documentación Principal](README.md)
- [Guía Docker + DVC](DOCKER_DVC_GUIDE.md)
- [Ejemplos Prácticos](EXAMPLES.md)
- [Checklist de Setup](SETUP_CHECKLIST.md)
- [Arquitectura del Sistema](ARCHITECTURE.md)

---

## ❓ ¿Tu pregunta no está aquí?

1. Busca en los issues de GitHub del proyecto
2. Consulta la documentación oficial de [DVC](https://dvc.org/doc) o [Docker](https://docs.docker.com/)
3. Pregunta a tu equipo
4. Crea un issue con tu pregunta para ayudar a otros
