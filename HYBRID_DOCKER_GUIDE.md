# 🚀 Hybrid Docker & DVC Orchestration Guide

**Version**: 3.0 (Hybrid)
**Status**: ✅ Production Ready
**Last Updated**: 2025-11-17

## Overview

This guide explains the new hybrid Dockerfile and docker-compose configuration that combines **ali's DVC orchestration capabilities** with **eze's modular architecture**. You now have the flexibility to run your entire ML pipeline through DVC while maintaining the clean, modular structure of your services.

---

## 🎯 What You Get

### ✅ From ali (DVC Orchestration)
- **`dvc repro`** support - Execute entire pipeline with dependency management
- **AWS CLI v2** integration - Full S3 interaction capabilities
- **Multi-backend DVC** support (S3, GCS, Azure)
- **Pinned DVC version** (3.55.2) for reproducibility
- **DVC remote configuration** via environment variables

### ✅ From eze (Modular Architecture)
- **Clean separation of concerns** - Each service has a specific purpose
- **Profile-based execution** - Run only what you need
- **Drift detection** as first-class services
- **Independent service scaling** - Run stages manually or via DVC
- **API & monitoring** integrated into the stack

### 🆕 New Features
- **Smart entrypoint** - Auto-configures DVC remotes
- **Dual execution modes**:
  - **Orchestrated**: `docker-compose run dvc-pipeline` (DVC manages execution)
  - **Manual**: Run individual services independently
- **Profile system** - Organize services by purpose (pipeline, manual, drift, services, test, dev)
- **Optimized volumes** - Selective mount strategies per service

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                        │
│                    (ml-network: 172.28.0.0/16)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PIPELINE SERVICES (profiles: pipeline, manual)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  dvc-pipeline ──────→ [DVC REPRO: Manages all stages]           │
│  (dvc repro)                                                      │
│                                                                   │
│  OR (Manual Orchestration):                                       │
│  dvc-pull ──→ eda-pipeline ──→ ml-pipeline ──→ compare           │
│       ↓                ↓              ↓            ↓              │
│    visualize ←────────┴──────────────┘────────────┘              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DRIFT SERVICES (profiles: drift)                                 │
├─────────────────────────────────────────────────────────────────┤
│  simulate-drift ──→ detect-drift ──→ visualize-drift             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SERVICE LAYER (profiles: services)                               │
├─────────────────────────────────────────────────────────────────┤
│  api (FastAPI @ :8000)    ·    mlflow (UI @ :5001)              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TESTING (profiles: test)                                         │
├─────────────────────────────────────────────────────────────────┤
│  test (pytest with coverage)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT (profiles: dev)                                      │
├─────────────────────────────────────────────────────────────────┤
│  shell (interactive bash)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create .env file with AWS credentials (for DVC S3 remote)
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DVC_REMOTE_NAME=myremote
DVC_REMOTE_URL=s3://your-bucket/obesity-ml
EOF

# Initialize git (if not already done)
git init
git config user.email "mlops@equipo52.com"
git config user.name "MLOps Team"
```

### 2. Run Complete Pipeline via DVC (Recommended)

```bash
# Build image and run entire DVC pipeline with automatic dependency management
docker-compose run dvc-pipeline

# Output includes:
# ✅ dvc pull (fetch data/models)
# ✅ eda (EDA stages from dvc.yaml)
# ✅ train (training stages)
# ✅ evaluate (evaluation stages)
# ✅ detect_drift (drift detection)
# ✅ visualize_drift (drift visualization)
```

**What happens**:
- Dockerfile entrypoint configures DVC remote
- AWS credentials loaded from `.env`
- `dvc repro` executes all stages in `dvc.yaml` in correct order
- Outputs stored in volumes (data/, models/, reports/)

### 3. Run Individual Services (Manual Mode)

```bash
# Pull data from remote first
docker-compose run dvc-pull

# Run individual stages (only the ones you need)
docker-compose run eda-pipeline
docker-compose run ml-pipeline
docker-compose run compare
docker-compose run visualize
```

### 4. Run Drift Detection

```bash
# Run drift simulation, detection, and visualization
docker-compose run --profile drift simulate-drift
docker-compose run --profile drift detect-drift
docker-compose run --profile drift visualize-drift
```

### 5. Start API & Monitoring

```bash
# Start API server and MLflow in background
docker-compose up -d --profile services api mlflow

# Access:
# - API docs: http://localhost:8000/docs
# - MLflow UI: http://localhost:5001
# - Health check: curl http://localhost:8000/health
```

### 6. Run Tests

```bash
docker-compose run --profile test test
```

### 7. Interactive Development

```bash
# Start interactive shell with full project mounted
docker-compose run --profile dev shell

# Inside container:
# $ python scripts/run_eda.py
# $ dvc repro
# $ dvc status
# $ exit
```

---

## 📋 Service Reference

### Pipeline Services

| Service | Profile | Command | Purpose | Dependencies |
|---------|---------|---------|---------|--------------|
| **dvc-pipeline** | `pipeline` | `dvc repro` | Run entire DVC pipeline | None (self-contained) |
| **dvc-pull** | `default` | `dvc pull` | Fetch data/models from remote | None |
| **eda-pipeline** | `manual` | `python scripts/run_eda.py` | Exploratory Data Analysis | dvc-pull |
| **ml-pipeline** | `manual` | `python scripts/run_ml.py` | Model training | dvc-pull, eda-pipeline |
| **compare** | `manual` | `python scripts/compare_datasets.py` | Dataset validation | dvc-pull |
| **visualize** | `manual` | `python scripts/generate_visualizations.py` | Generate plots | dvc-pull |

### Drift Services

| Service | Profile | Command | Purpose | Dependencies |
|---------|---------|---------|---------|--------------|
| **simulate-drift** | `drift` | `python scripts/simulate_drift.py` | Create drifted dataset | dvc-pull |
| **detect-drift** | `drift` | `python scripts/detect_drift.py` | Detect data drift | simulate-drift |
| **visualize-drift** | `drift` | `python scripts/visualize_drift.py` | Visualize drift | detect-drift |

### API & Monitoring

| Service | Profile | Command | Port | Purpose |
|---------|---------|---------|------|---------|
| **api** | `services` | `uvicorn src.api.main:app ...` | 8000 | FastAPI server |
| **mlflow** | `services` | `mlflow ui ...` | 5001 | Experiment tracking |

### Testing & Development

| Service | Profile | Command | Purpose |
|---------|---------|---------|---------|
| **test** | `test` | `pytest tests/ -v --cov=src` | Run test suite |
| **shell** | `dev` | `bash` | Interactive development |

---

## 💡 Usage Patterns

### Pattern 1: Full Automated Pipeline

```bash
# One command to run everything
docker-compose run dvc-pipeline

# Equivalent to running manually:
# docker-compose run dvc-pull
# docker-compose run eda-pipeline
# docker-compose run ml-pipeline
# ... (all other stages)
```

**Best for**: CI/CD, batch processing, production runs

---

### Pattern 2: Development with Manual Control

```bash
# Pull data once
docker-compose run dvc-pull

# Work on EDA in isolation
docker-compose run eda-pipeline

# When ready, train models
docker-compose run ml-pipeline

# Run API separately for testing
docker-compose up -d api
```

**Best for**: Experimentation, debugging, development

---

### Pattern 3: API-Centric Workflow

```bash
# Ensure data is ready
docker-compose run dvc-pull

# Start API and MLflow
docker-compose up -d --profile services

# In another terminal, start monitoring
docker-compose up -d --profile services mlflow

# Test your API
curl http://localhost:8000/docs

# Logs
docker-compose logs -f api
```

**Best for**: API development, model serving

---

### Pattern 4: Monitoring & Alerts

```bash
# Run drift detection pipeline
docker-compose run --profile drift dvc-pull
docker-compose run --profile drift simulate-drift
docker-compose run --profile drift detect-drift
docker-compose run --profile drift visualize-drift

# Check reports/
# - reports/drift_report.json (machine-readable)
# - reports/drift_alerts.txt (human-readable)
```

**Best for**: Production monitoring, data quality

---

## 🔧 Configuration

### Environment Variables

Create `.env` file or export variables:

```bash
# AWS/DVC Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DVC_REMOTE_NAME=myremote        # Default: myremote
DVC_REMOTE_URL=s3://bucket/path # Default: not set

# Optional: Override DVC version
# DVC_VERSION=3.55.2

# Optional: API Configuration
API_VERSION=1.0.0
API_HOST=0.0.0.0
API_PORT=8000

# Optional: MLflow Configuration
MLFLOW_PORT=5001
```

### DVC Configuration

The Dockerfile entrypoint automatically configures DVC when you provide:

```bash
# In .env or environment
DVC_REMOTE_NAME=myremote
DVC_REMOTE_URL=s3://your-bucket/obesity-ml
```

This runs inside the container:
```bash
dvc remote add -d myremote s3://your-bucket/obesity-ml
```

---

## 📊 Volume Mounts Strategy

### Pipeline Services (Generous Mounts)
Services that need full access for processing:
```yaml
volumes:
  - ./data:/app/data
  - ./models:/app/models
  - ./reports:/app/reports
  - ./mlruns:/app/mlruns
  - ./.dvc:/app/.dvc
```

### API Service (Minimal, Read-Only)
API only needs to read models:
```yaml
volumes:
  - ./models:/app/models:ro      # Read-only
  - ./mlruns:/app/mlruns:ro      # Read-only
  - ./src/api:/app/src/api       # For hot-reload
```

### Drift Services (Specific Mounts)
Only data and reports needed:
```yaml
volumes:
  - ./data:/app/data
  - ./reports:/app/reports
```

This strategy:
- ✅ Prevents accidental modifications
- ✅ Improves security
- ✅ Reduces I/O overhead
- ✅ Makes dependencies explicit

---

## 🐛 Troubleshooting

### Issue: "DVC remote not configured"

```bash
# Solution 1: Ensure .env file exists
echo "DVC_REMOTE_URL=s3://your-bucket/path" >> .env

# Solution 2: Manually configure inside container
docker-compose run shell
# Inside container:
dvc remote add -d myremote s3://your-bucket/path
exit
```

### Issue: "Permission denied" on data files

```bash
# DVC and git might change permissions. Fix with:
docker-compose run shell
# Inside:
chmod -R 755 data/
chmod -R 755 models/
exit
```

### Issue: Out of disk space

```bash
# Clear DVC cache
docker-compose run shell
# Inside:
dvc gc --workspace --force
exit

# Or prune Docker
docker system prune -a
```

### Issue: AWS credentials not working

```bash
# Verify credentials in .env
echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
echo "AWS_SECRET_ACCESS_KEY is set: $([ -n "$AWS_SECRET_ACCESS_KEY" ] && echo yes || echo no)"

# Test S3 access
docker-compose run shell
# Inside:
aws s3 ls s3://your-bucket/
exit
```

---

## 📈 Performance Optimization

### 1. Build Cache Strategy

```bash
# First build (slow)
docker-compose build

# Subsequent builds (fast, uses cache)
# Only changed layers are rebuilt
```

**Optimize** by keeping Dockerfile order:
1. Base image
2. System dependencies
3. requirements.txt (change infrequently)
4. DVC (change infrequently)
5. Project files (change frequently)

### 2. Volume Performance

```bash
# On Docker Desktop (Windows/Mac), use bind mounts for code:
volumes:
  - ./src:/app/src         # Fast (bind mount)
  - ./models:/app/models   # Fast (bind mount)

# Avoid slow operations:
volumes:
  - ./data:/app/data:delegated  # Delayed sync (macOS only)
```

### 3. Parallel Execution

```bash
# Run independent services in parallel
docker-compose up -d api mlflow
docker-compose run --profile manual eda-pipeline &
docker-compose run --profile manual ml-pipeline &
wait

# Wait for both to complete
```

---

## 🔒 Security Considerations

### ✅ Implemented
- ✅ AWS credentials in `.env` (not in Dockerfile)
- ✅ `.env` in `.gitignore` (prevent accidental commit)
- ✅ Read-only mounts for API service
- ✅ Limited container privileges

### 🔐 Recommended for Production

```bash
# 1. Use AWS IAM roles instead of long-term credentials
# 2. Use Docker secrets for sensitive data
# 3. Implement authentication on API
# 4. Add rate limiting
# 5. Use private Docker registry
# 6. Enable audit logging
```

See [src/api/README.md](src/api/README.md) for API security details.

---

## 📝 Common Commands

```bash
# View all services and their status
docker-compose ps -a

# View service logs
docker-compose logs -f api
docker-compose logs dvc-pipeline

# Stop all containers
docker-compose down

# Remove volumes (warning: deletes data)
docker-compose down -v

# Rebuild image
docker-compose build --no-cache

# Check DVC status
docker-compose run shell dvc status

# Add DVC stage
docker-compose run shell dvc add data/raw/data.csv

# List DVC remotes
docker-compose run shell dvc remote list
```

---

## 🎯 Best Practices

### 1. Always Pull Before Running
```bash
docker-compose run dvc-pull
```

### 2. Use Profiles for Organization
```bash
# Don't start all services at once
docker-compose up -d                    # Only default services
docker-compose up -d --profile services # Start API + MLflow
docker-compose run --profile test test  # Run tests only
```

### 3. Check Service Dependencies
```bash
# Before running a service, ensure its dependencies are ready
# Example: ml-pipeline depends on dvc-pull and eda-pipeline
docker-compose run dvc-pull
docker-compose run eda-pipeline
docker-compose run ml-pipeline
```

### 4. Monitor Logs
```bash
# Keep logs visible during pipeline execution
docker-compose logs -f dvc-pipeline
```

### 5. Version Control Configuration
```bash
# Commit docker-compose.yml and Dockerfile
git add Dockerfile docker-compose.yml
git commit -m "Update hybrid Docker configuration"

# Don't commit .env
# Already in .gitignore
```

---

## 🚀 Advanced Usage

### Run Specific DVC Stage

```bash
docker-compose run dvc-pipeline dvc repro stages.eda
```

### Debug DVC Pipeline

```bash
docker-compose run dvc-pipeline dvc dag
```

### Custom Entry Point

```bash
# Override default command
docker-compose run dvc-pipeline bash
```

### Execute Multiple Services Sequentially

```bash
docker-compose run dvc-pull && \
docker-compose run eda-pipeline && \
docker-compose run ml-pipeline && \
docker-compose run api
```

---

## 📚 Related Documentation

- [API Architecture](src/api/README.md) - FastAPI modular design
- [Drift Detection Guide](README_DRIFT_DETECTION.md) - Monitoring setup
- [DVC Documentation](https://dvc.org) - Data versioning
- [Docker Compose Reference](https://docs.docker.com/compose) - Official docs

---

## ✅ Checklist for First Run

- [ ] Clone repository: `git clone ...`
- [ ] Create `.env` file with AWS credentials
- [ ] Build Docker image: `docker-compose build`
- [ ] Test DVC remote: `docker-compose run dvc-pull`
- [ ] Run full pipeline: `docker-compose run dvc-pipeline`
- [ ] Check outputs: `ls -la data/ models/ reports/`
- [ ] Start API: `docker-compose up -d --profile services api`
- [ ] Test API: `curl http://localhost:8000/health`
- [ ] View logs: `docker-compose logs -f api`

---

## 🎉 Summary

You now have a production-ready, hybrid Docker & DVC setup that provides:

| Feature | Benefit |
|---------|---------|
| **DVC Pipeline Orchestration** | Automatic dependency management, reproducible runs |
| **Modular Architecture** | Run services independently or as a unified pipeline |
| **Profile System** | Organize services by purpose (pipeline, drift, services, etc.) |
| **Environment Configuration** | Flexible setup via .env |
| **Multi-Backend Support** | S3, GCS, Azure, local storage |
| **API Integration** | FastAPI server with health checks |
| **Monitoring** | MLflow tracking, drift detection, visualization |
| **Development Ready** | Interactive shell, hot-reload, test suite |

**Start using it**:
```bash
docker-compose run dvc-pipeline
```

That's it! Everything else is automatic. 🚀

---

**Version**: 3.0-hybrid
**Status**: ✅ Production Ready
**Tested**: Yes
**Last Updated**: 2025-11-17
**Maintainer**: MLOps Team - Equipo 52
