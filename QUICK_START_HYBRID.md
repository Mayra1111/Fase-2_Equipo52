# ⚡ Quick Start: Hybrid Docker Setup

**TL;DR** - Get running in 5 minutes

---

## 🚀 5-Minute Setup

### Step 1: Setup Environment (1 min)

```bash
# Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DVC_REMOTE_NAME=myremote
DVC_REMOTE_URL=s3://your-bucket/obesity-ml
EOF

# Or if using local storage (testing)
cat > .env << EOF
DVC_NO_ANALYTICS=1
EOF
```

### Step 2: Build Image (2-3 min)

```bash
docker-compose build
```

### Step 3: Run Pipeline (1 min)

```bash
# Option A: Automated (DVC manages everything)
docker-compose run dvc-pipeline

# OR Option B: Manual (control each stage)
docker-compose run dvc-pull
docker-compose run eda-pipeline
docker-compose run ml-pipeline
```

### Step 4: Start API (1 min)

```bash
docker-compose up -d --profile services api
# Access: http://localhost:8000/docs
```

**Done!** ✅

---

## 📋 Common Commands Cheat Sheet

### Run Everything (Automated)
```bash
docker-compose run dvc-pipeline
```

### Run Individual Stages
```bash
docker-compose run dvc-pull          # Fetch data
docker-compose run eda-pipeline      # Explore data
docker-compose run ml-pipeline       # Train model
docker-compose run api               # Start serving
```

### Run Drift Detection
```bash
docker-compose run --profile drift simulate-drift
docker-compose run --profile drift detect-drift
docker-compose run --profile drift visualize-drift
```

### Check Status
```bash
docker-compose ps                    # Running containers
docker-compose logs -f api           # Watch API logs
docker-compose run shell dvc status # Check DVC state
```

### Cleanup
```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop + remove volumes
docker system prune -a     # Clean up everything
```

---

## 🎯 Three Execution Patterns

### Pattern 1: Full Automation (Recommended for CI/CD)
```bash
# One command, complete pipeline
docker-compose run dvc-pipeline
```

### Pattern 2: Manual Control (For Development)
```bash
# Run each stage separately
docker-compose run dvc-pull
docker-compose run eda-pipeline
docker-compose run ml-pipeline
docker-compose run api
```

### Pattern 3: Interactive Development
```bash
# Get shell access to container
docker-compose run --profile dev shell

# Inside container:
$ dvc repro
$ python scripts/run_eda.py
$ exit
```

---

## 🔍 Verify It Works

### Check Pipeline
```bash
# Ensure all services are healthy
docker-compose ps

# Should see:
# dvc-pull              Exited (0)
# eda-pipeline          Exited (0)
# ml-pipeline           Exited (0)
# [etc... all with exit code 0]
```

### Check API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy",...}

# View API docs
# Open browser: http://localhost:8000/docs
```

### Check Data
```bash
# Verify outputs created
ls -la data/
ls -la models/
ls -la reports/
```

---

## ❌ Troubleshooting (2 min)

### Problem: "DVC remote not configured"
```bash
# Add these to .env:
DVC_REMOTE_NAME=myremote
DVC_REMOTE_URL=s3://your-bucket/path

# Then retry
docker-compose build
docker-compose run dvc-pull
```

### Problem: "Permission denied"
```bash
# Fix permissions inside container
docker-compose run shell chmod -R 755 data/ models/
```

### Problem: "Out of disk space"
```bash
# Clean DVC cache
docker-compose run shell dvc gc --workspace --force

# Or clean Docker
docker system prune -a
```

### Problem: "AWS credentials not working"
```bash
# Test credentials
docker-compose run shell
# Inside:
$ aws s3 ls s3://your-bucket/
# If fails, check .env file has correct AWS_* values
```

---

## 📊 Performance Tips

### 1. Reuse Volumes (Faster)
```bash
# Don't delete volumes between runs
docker-compose down     # Stop but keep volumes
docker-compose up       # Restart quickly

# Only clear when needed:
docker-compose down -v  # Delete volumes
```

### 2. Build Once
```bash
# First build (slow):
docker-compose build

# Subsequent runs use cache (fast):
docker-compose run dvc-pipeline
```

### 3. Check Build Status
```bash
# If builds are slow, check what's happening
docker buildx build --progress=plain -t obesity-ml .
```

---

## 🎓 Understanding the Architecture

```
┌─────────────────────────────────────────┐
│  docker-compose run dvc-pipeline        │
│           (orchestrated mode)           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Image: python:3.10-slim                │
│  + DVC (S3, GCS, Azure support)        │
│  + AWS CLI v2                           │
│  + Project code                         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  DVC Smart Entrypoint                   │
│  • Configures S3 remote from .env       │
│  • Sets AWS credentials                 │
│  • Executes: dvc repro                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  dvc.yaml Stages (in order):            │
│  1. eda          (EDA)                  │
│  2. train        (Model training)       │
│  3. evaluate     (Model evaluation)     │
│  4. detect_drift (Drift detection)      │
│  5. visualize    (Generate plots)       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Outputs (in host volumes):             │
│  • data/          (processed data)      │
│  • models/        (trained models)      │
│  • reports/       (plots & metrics)     │
│  • mlruns/        (MLflow tracking)     │
└─────────────────────────────────────────┘
```

---

## 🔒 Security Checklist

- [ ] `.env` is in `.gitignore` (don't commit credentials)
- [ ] Use IAM roles instead of long-term keys for production
- [ ] API runs with read-only models volume (no modification)
- [ ] Use environment variables for all secrets
- [ ] Enable Docker Health Checks

---

## 📱 Docker Desktop (Windows/Mac) Tips

### Enable WSL 2 (Windows)
```bash
# In PowerShell (Admin):
wsl --install

# Set WSL2 as default:
wsl --set-default-version 2
```

### Increase Resources
- Docker Desktop → Settings → Resources
- CPU: 4+ cores
- Memory: 8+ GB
- Disk: 20+ GB

### Performance
- Use bind mounts for code (fast)
- Store data in Docker volumes (slower but reliable)

---

## 📚 Next Steps

### After First Run:
1. ✅ Check outputs in `reports/`, `data/`, `models/`
2. ✅ Review metrics in MLflow UI
3. ✅ Test API at http://localhost:8000/docs
4. ✅ Check drift alerts in `reports/drift_alerts.txt`

### For Development:
1. 📖 Read [HYBRID_DOCKER_GUIDE.md](HYBRID_DOCKER_GUIDE.md) for full details
2. 🔧 Check [dvc.yaml](dvc.yaml) for pipeline stages
3. 🧪 See [tests/](tests/) for test examples

### For Production:
1. 🔐 Review security in [src/api/README.md](src/api/README.md)
2. 📊 Setup monitoring (MLflow, drift detection)
3. 🚀 Deploy with Kubernetes or cloud platform

---

## ⏱️ Typical Run Times

| Command | Time | Notes |
|---------|------|-------|
| `docker-compose build` | 3-5 min | First time only |
| `docker-compose run dvc-pipeline` | 5-15 min | Full pipeline |
| `docker-compose run dvc-pull` | 1-2 min | Fetch data |
| `docker-compose run eda-pipeline` | 2-3 min | Explore data |
| `docker-compose run ml-pipeline` | 3-5 min | Train model |
| `docker-compose up api` | <1 min | Start API |

---

## 🆘 Getting Help

### Check Logs
```bash
# See what went wrong
docker-compose logs dvc-pipeline
docker-compose logs api
docker-compose logs mlflow
```

### Run Shell
```bash
# Debug inside container
docker-compose run --profile dev shell

# Inside container, try:
$ dvc status
$ dvc dag
$ python -c "import src; print(src.__version__)"
```

### Full Documentation
- Detailed guide: [HYBRID_DOCKER_GUIDE.md](HYBRID_DOCKER_GUIDE.md)
- API reference: [src/api/README.md](src/api/README.md)
- Drift detection: [README_DRIFT_DETECTION.md](README_DRIFT_DETECTION.md)
- Comparison: [THREE_APPROACHES_COMPARISON.md](THREE_APPROACHES_COMPARISON.md)

---

## ✅ Success Checklist

After setup, you should have:

- [ ] `.env` file with AWS credentials
- [ ] Docker image built (`docker-compose build` completed)
- [ ] Pipeline ran successfully (`docker-compose run dvc-pipeline` completed)
- [ ] Data in `data/` directory
- [ ] Models in `models/` directory
- [ ] Reports in `reports/` directory
- [ ] API running at http://localhost:8000
- [ ] Drift detection completed
- [ ] All tests passing (`docker-compose run --profile test test`)

**You're ready to go!** 🚀

---

## 🎯 One-Liner Examples

```bash
# Run everything (most common)
docker-compose run dvc-pipeline

# Just pull data
docker-compose run dvc-pull

# Just train models
docker-compose run dvc-pull && docker-compose run ml-pipeline

# Run API server
docker-compose up -d --profile services api

# Run tests
docker-compose run --profile test test

# Debug in shell
docker-compose run --profile dev shell

# Check status
docker-compose ps

# Stop everything
docker-compose down

# Clean everything
docker-compose down -v && docker system prune -a
```

---

**Version**: 3.0-hybrid
**Last Updated**: 2025-11-17
**Status**: Ready to use
**Complexity**: ⭐ Easy (automated setup)
