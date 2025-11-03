# Obesity ML Project - Installation and Setup Guide

## Overview

This project implements a complete Machine Learning pipeline for obesity estimation, following professional MLOps practices. The codebase has been refactored from a Jupyter notebook into a modular, maintainable structure using Object-Oriented Programming principles and Scikit-Learn pipelines.

## Team Members and Responsibilities

| Student ID | Name | Role | Primary Responsibilities |
|------------|------|------|--------------------------|
| A01796095 | Alicia Yovanna Canta Pandal | DevOps Engineer | Docker containerization, CI/CD pipelines, infrastructure setup, Docker Compose orchestration, DVC integration with AWS S3 |
| A01067109 | Iván Ricardo Cruz Ibarra | Data Scientist | Data analysis, statistical validation, EDA methodology, data quality assessment |
| A01796828 | Mayra Hernández Alba | Data Engineer | Data loading modules (`data_loader.py`), data cleaning pipelines (`data_cleaner.py`), data preprocessing |
| A01212428 | Sebastián Ezequiel Coronado Rivera | ML Engineer | Model training (`model_trainer.py`), ML pipeline orchestration (`ml_pipeline.py`), MLflow integration, experiment tracking, project structure, code architecture, testing framework |

### Detailed Responsibilities by Role and Module

**DevOps Engineer (Alicia Canta Pandal):**
- `Dockerfile` - Container image definition, dependency installation, environment setup
- `docker-compose.yml` - Service orchestration, volume configuration, network setup (including DVC service integration)
- `.gitignore`, `.dvcignore` - Version control configuration
- DVC integration with AWS S3 - Configuration and setup of data version control with remote S3 storage
- `scripts/dvc_setup.sh` and `scripts/dvc_setup.ps1` - DVC initialization and S3 remote configuration scripts
- `scripts/dvc_pull_data.sh` - Script for pulling data from S3 bucket
- `scripts/dvc_push_artifacts.sh` - Script for pushing data and models to S3 bucket
- `.dvc/config` - DVC remote configuration for AWS S3 (s3://itesm-mna/202502-equipo52)
- Infrastructure setup, containerization strategy, and cloud storage integration

**ML Engineer (Sebastián Coronado Rivera):**
- Project structure following Cookiecutter template
- `setup.py` - Package configuration and distribution
- `src/utils/config.py` - Centralized configuration management
- `src/utils/logger.py` - Logging system implementation
- `tests/test_comparison.py` - EDA pipeline validation tests
- `tests/test_ml_pipeline.py` - ML pipeline validation tests
- Code architecture and refactoring patterns

**Data Engineer (Mayra Hernández Alba):**
- `src/data/data_loader.py` - Data loading infrastructure with error handling
- `src/data/data_cleaner.py` - Data cleaning pipeline with Scikit-Learn transformers
- Data preprocessing pipelines and data quality assurance
- DVC integration for data versioning

**Data Scientist (Iván Cruz Ibarra):**
- `pipelines/eda_pipeline.py` - EDA pipeline orchestration and MLflow integration
- `src/visualization/eda_visualizer.py` - Statistical visualizations and exploratory analysis
- EDA methodology and data quality assessment
- Statistical validation and results interpretation
- `notebooks/EDA.ipynb` - Initial exploratory analysis

**ML Engineer (Sebastián Coronado Rivera):**
- `src/models/model_trainer.py` - Model training with multiple algorithms and hyperparameter tuning
- `src/models/data_preprocessor.py` - Feature preprocessing for ML models
- `src/models/model_evaluator.py` - Model evaluation metrics and comparison
- `pipelines/ml_pipeline.py` - Complete ML pipeline orchestration
- MLflow experiment tracking and model registry
- `scripts/run_ml.py` - ML pipeline execution script
- `scripts/version_models.sh` - Script for versioning trained models with DVC

## Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Git** - For cloning the repository
2. **Docker Desktop** - Version 20.10 or higher (required for containerized execution)
3. **Python 3.10+** (optional, if running without Docker)
4. **Git client** - For version control operations

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd refactored_mlops
```

### Step 2: Install Docker Desktop

**Windows:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Launch Docker Desktop and wait for it to fully start (you'll see "Docker Desktop is running" in the system tray)

**macOS:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Drag Docker.app to Applications folder
3. Open Docker from Applications and wait for initialization

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Verify Docker Installation

Open a terminal and verify Docker is working:

```bash
docker --version
docker compose version
docker ps
```

The `docker ps` command should execute without errors (it may show an empty list, which is normal).

### Step 4: Create Required Directories

Docker Compose mounts several directories as volumes. These directories must exist before running containers:

```bash
# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path models, reports\figures, reports\metrics, mlruns

# Linux/macOS
mkdir -p models reports/figures reports/metrics mlruns
```

**Why these directories?**
- `models/` - Stores trained ML models (.pkl, .joblib files)
- `reports/figures/` - Contains visualization outputs (PNG files)
- `reports/metrics/` - Stores evaluation metrics and reports
- `mlruns/` - MLflow tracking database and experiment artifacts

These directories are mounted as volumes in Docker Compose, allowing data persistence between container runs and enabling file sharing between the container and your local filesystem.

### Step 5: Build Docker Images

Build the Docker images for all services:

```bash
docker compose build
```

**Time estimate:** 5-10 minutes on first execution (subsequent builds will be faster due to layer caching)

**What happens during build:**
- Docker reads the `Dockerfile` and `requirements.txt`
- Downloads Python 3.10 base image
- Installs system dependencies (git, curl)
- Installs Python packages from `requirements.txt`
- Copies project files into the container
- Installs the package in development mode with `pip install -e .`
- Creates necessary directory structure inside the container

You should see progress output ending with:
```
[+] Building X.Xs (X/X) FINISHED
```

### Step 6: Configure DVC and AWS S3 (Optional but Recommended)

The project uses DVC (Data Version Control) for managing datasets and models, with AWS S3 as remote storage. This allows team members to share data and models efficiently.

**Prerequisites for DVC:**
- AWS account with S3 bucket access
- AWS credentials (Access Key ID and Secret Access Key)
- Bucket name: `itesm-mna/202502-equipo52`

**Setup DVC with S3:**

**Windows (PowerShell):**
```powershell
# Create .env file with AWS credentials (if not exists)
# Copy from .env.example and fill in your AWS credentials

# Run DVC setup script
.\scripts\dvc_setup.ps1
```

**Linux/macOS:**
```bash
# Create .env file with AWS credentials (if not exists)
# Copy from .env.example and fill in your AWS credentials

# Run DVC setup script
chmod +x scripts/dvc_setup.sh
./scripts/dvc_setup.sh
```

**What the setup script does:**
- Initializes DVC repository (if not already initialized)
- Configures S3 remote storage connection
- Sets up AWS credentials in DVC configuration
- Tests S3 connection

**Pull data from S3 (if available):**
```bash
# Windows
.\scripts\dvc_pull_data.sh

# Linux/macOS
./scripts/dvc_pull_data.sh
```

**Note:** If you don't have AWS credentials or prefer to work with local data only, you can skip this step. The Docker Compose setup includes a `dvc-pull` service that automatically pulls data from S3 before running pipelines (if configured).

### Step 7: Verify Data Files

Ensure the following data files exist in `data/interim/`:
- `obesity_estimation_modified.csv` - Input dataset with data quality issues
- `obesity_estimation_original.csv` - Reference dataset for comparison

If using DVC, these files will be automatically pulled from S3 when you run `dvc pull` or when Docker Compose executes the `dvc-pull` service.

## Running the Project

### Option 1: Complete Workflow (Recommended for First Run)

Execute the complete pipeline including EDA, validation, and testing:

```bash
docker compose run --rm eda-pipeline
docker compose run --rm compare
docker compose run --rm test
```

### Option 2: Individual Services

**EDA Pipeline (Data Cleaning):**
```bash
docker compose run --rm eda-pipeline
```
This executes the data cleaning pipeline, generating `data/interim/dataset_limpio_refactored.csv`.

**ML Pipeline (Model Training):**
```bash
docker compose run --rm ml-pipeline
```
Note: This requires the EDA pipeline to have completed first.

**Dataset Comparison:**
```bash
docker compose run --rm compare
```
Compares the original cleaned dataset with the refactored version to validate identical results.

**Visualization Generation:**
```bash
docker compose run --rm visualize
```
Generates EDA visualizations saved in `reports/figures/`.

**Unit Tests:**
```bash
docker compose run --rm test
```
Executes all unit tests using pytest.

**MLflow UI:**
```bash
docker compose up mlflow
```
Starts the MLflow tracking server. Access the UI at http://localhost:5000

**Interactive Shell:**
```bash
docker compose run --rm shell
```
Provides an interactive bash shell inside the container for development and debugging.

### Option 3: Using Helper Scripts

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\docker-run.ps1 all
```

**Linux/macOS:**
```bash
chmod +x docker-run.sh
./docker-run.sh all
```

## Expected Outputs

After executing the pipeline, you should find:

- `data/interim/dataset_limpio_refactored.csv` - Cleaned dataset (2153 rows, 17 columns, 0 missing values)
- `models/` - Directory containing trained models (after ML pipeline execution)
- `reports/figures/` - Visualization PNG files
- `reports/metrics/` - JSON/TXT files with evaluation metrics
- `mlruns/` - MLflow experiment database

## Validation

The project includes comprehensive validation to ensure the refactored code produces identical results to the original notebook:

**Dataset Comparison:**
- Shape validation: (2153, 17) for both original and refactored
- Column validation: All 17 columns match
- Data type validation: All dtypes identical
- Value validation: 100% identical values
- Missing values: 0 in both datasets

**Unit Tests:**
- 12 comprehensive tests covering all cleaning steps
- Automated validation using pytest
- All tests must pass to ensure correctness

Run validation:
```bash
docker compose run --rm compare
docker compose run --rm test
```

## Data Version Control with DVC and AWS S3

This project uses DVC (Data Version Control) integrated with AWS S3 for managing datasets and trained models. This setup allows team members to:

- Share large datasets and models without storing them in Git
- Track versions of data and models
- Automatically pull latest data when running pipelines in Docker
- Push new datasets/models to shared S3 storage

### DVC Configuration

The project is configured to use AWS S3 as the remote storage:
- **Remote name:** `team_remote`
- **S3 bucket:** `s3://itesm-mna/202502-equipo52`
- **Region:** `us-east-2`

### Using DVC Commands

**Setup (First time only):**
```bash
# Windows
.\scripts\dvc_setup.ps1

# Linux/macOS
./scripts/dvc_setup.sh
```

**Add datasets to DVC tracking:**
```bash
# Windows
.\scripts\dvc_add_data.ps1

# Linux/macOS
./scripts/dvc_add_data.sh
```

**Pull data from S3:**
```bash
# Windows
.\scripts\dvc_pull_data.sh

# Linux/macOS
./scripts/dvc_pull_data.sh

# Or use DVC directly
dvc pull
```

**Push data/models to S3:**
```bash
# Windows
.\scripts\dvc_push_artifacts.sh

# Linux/macOS
./scripts/dvc_push_artifacts.sh

# Or use DVC directly
dvc push
```

**Version models after training:**
```bash
# Linux/macOS
./scripts/version_models.sh
```

### Docker Integration

The `docker-compose.yml` includes a `dvc-pull` service that automatically pulls data from S3 before running pipelines. All services depend on `dvc-pull`, ensuring data is always up-to-date.

**Manual DVC pull in Docker:**
```bash
docker compose run --rm dvc-pull
```

### DVC Workflow

1. **Development:** Work with local data files
2. **Versioning:** Add files to DVC tracking (`dvc add`)
3. **Commit:** Commit `.dvc` metadata files to Git (not the actual data files)
4. **Push to S3:** Upload actual data files to S3 (`dvc push`)
5. **Share:** Team members pull data from S3 (`dvc pull`)

### Files Tracked by DVC

- `data/interim/*.csv` - Datasets (original, modified, cleaned)
- `models/*.pkl`, `models/*.joblib` - Trained ML models
- Metadata stored in `.dvc/` directory and `.dvc` files

## Troubleshooting

### Docker Desktop Not Running
**Error:** `Cannot connect to Docker daemon`

**Solution:** Open Docker Desktop and wait for it to fully initialize. Verify with `docker ps`.

### Missing Data Files
**Error:** `FileNotFoundError` when running pipelines

**Solution:** Ensure these files exist in `data/interim/`:
- `obesity_estimation_modified.csv`
- `obesity_estimation_original.csv`

**If using DVC:**
```bash
# Pull data from S3
dvc pull

# Or in Docker
docker compose run --rm dvc-pull
```

### DVC S3 Connection Issues
**Error:** `Failed to connect to S3` or `Access Denied`

**Solutions:**
1. Verify AWS credentials in `.env` file:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `AWS_S3_BUCKET`

2. Verify DVC remote configuration:
   ```bash
   dvc remote list
   dvc remote modify team_remote access_key_id YOUR_KEY
   dvc remote modify team_remote secret_access_key YOUR_SECRET
   ```

3. Test S3 connection:
   ```bash
   aws s3 ls s3://itesm-mna/202502-equipo52/
   ```

## Project Structure

```
refactored_mlops/
├── data/
│   ├── interim/          # Intermediate datasets
│   ├── notebooks/        # Jupyter notebooks
│   └── processed/        # Final processed data
├── models/               # Trained ML models
├── reports/
│   ├── figures/         # Visualization outputs
│   └── metrics/         # Evaluation metrics
├── mlruns/              # MLflow tracking database
├── src/                 # Source code
│   ├── data/            # Data loading and cleaning
│   ├── features/        # Feature engineering
│   ├── models/          # Model training and evaluation
│   ├── utils/           # Configuration and logging
│   └── visualization/   # EDA visualizations
├── pipelines/           # Complete pipeline orchestrations
├── scripts/            # Executable scripts
│   ├── dvc_*.sh/ps1   # DVC setup and management scripts
│   └── version_models.sh  # Model versioning with DVC
├── tests/              # Unit tests
├── .dvc/              # DVC configuration and cache
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Service orchestration
├── requirements.txt    # Python dependencies
└── setup.py           # Package configuration
```

## Key Features

- **Cookiecutter Template Structure** - Professional project organization
- **Object-Oriented Design** - Modular, maintainable code architecture
- **Scikit-Learn Pipelines** - Automated preprocessing pipeline
- **MLflow Integration** - Experiment tracking and model registry
- **Docker Containerization** - Reproducible execution environment
- **Comprehensive Testing** - Automated validation suite
- **DVC Integration with AWS S3** - Data version control with cloud storage for datasets and models

## Technical Stack

- **Language:** Python 3.10
- **ML Framework:** Scikit-Learn, XGBoost
- **Tracking:** MLflow 2.8.0
- **Containerization:** Docker, Docker Compose
- **Testing:** Pytest
- **Data Processing:** Pandas, NumPy
- **Data Version Control:** DVC 3.30.0 with AWS S3 remote storage
- **Cloud Storage:** AWS S3 (bucket: `itesm-mna/202502-equipo52`)

## Contributing

Each team member is responsible for maintaining and updating their assigned modules:

1. Work on feature branches
2. Test your changes: `docker compose run --rm test`
3. Ensure all tests pass before committing
4. Update documentation for significant changes
5. Coordinate with team members when changes affect shared modules

## Validation Results

The refactored pipeline has been validated to produce identical results to the original notebook:

- **Dataset Shape:** (2153, 17) ✓
- **Columns:** 17 columns, all matching ✓
- **Data Types:** All dtypes identical ✓
- **Values:** 100% identical values ✓
- **Missing Values:** 0 in both datasets ✓
- **Unit Tests:** 12/12 passed ✓

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please contact the respective team member based on the module in question, or refer to the team member list above for role-specific inquiries.

