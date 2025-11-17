# Dockerfile for Obesity ML Project - Hybrid DVC Orchestration
# Combines ali's DVC orchestration capabilities with eze's modular architecture
# Supports both direct script execution and DVC pipeline orchestration

FROM python:3.10-slim

# Container metadata
LABEL maintainer="MLOps Equipo 52"
LABEL description="ML Pipeline with DVC Orchestration for Obesity Classification"
LABEL version="3.0-hybrid"

# Set working directory
WORKDIR /app

# Install system dependencies (minimal + essential tools)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2 (enables S3 interactions for DVC)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies with upgrade
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install DVC with multi-backend support (S3, GCS, Azure)
# Using 3.55.2 (stable version, pinned for reproducibility)
RUN pip install --no-cache-dir 'dvc[s3,gs,azure]==3.55.2'

# Copy project files
COPY . .

# Install the package in development mode (editable install)
RUN pip install -e .

# Create necessary directories for data pipeline and outputs
RUN mkdir -p \
    data/raw \
    data/interim \
    data/processed \
    models \
    reports/figures \
    reports/metrics \
    mlruns \
    .dvc/cache \
    config

# Configure Git (required by DVC)
RUN git config --global user.email "mlops@equipo52.com" && \
    git config --global user.name "MLOps Team" && \
    git config --global --add safe.directory /app

# Set Python path for imports
ENV PYTHONPATH=/app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DVC_NO_ANALYTICS=1

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

# Create DVC entrypoint script that configures remotes before execution
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Configure DVC Remote if environment variables provided\n\
if [ ! -z "$DVC_REMOTE_URL" ] && [ ! -z "$DVC_REMOTE_NAME" ]; then\n\
  echo "=== Configuring DVC Remote ==="\n\
  dvc remote add -d $DVC_REMOTE_NAME $DVC_REMOTE_URL -f 2>/dev/null || true\n\
  echo "DVC remote configured: $DVC_REMOTE_NAME -> $DVC_REMOTE_URL"\n\
fi\n\
\n\
# Configure AWS credentials if provided\n\
if [ ! -z "$AWS_ACCESS_KEY_ID" ]; then\n\
  echo "AWS credentials configured from environment variables"\n\
fi\n\
\n\
echo "=== Entrypoint setup complete ==="\n\
echo "Executing: $@"\n\
exec "$@"\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command: Run DVC pipeline (can be overridden in docker-compose or docker run)
CMD ["dvc", "repro"]
