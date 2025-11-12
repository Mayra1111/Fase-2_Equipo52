# Dockerfile for Obesity ML Project with DVC Orchestration
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Metadatos del contenedor
LABEL maintainer="MLOps Equipo 52"
LABEL description="ML Pipeline con DVC para clasificación de obesidad"
LABEL version="3.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install DVC with S3 support and additional backends
# Using 3.55.2 (latest stable version without umask bug)
RUN pip install --no-cache-dir 'dvc[s3,gs,azure]==3.55.2'

# Copy project files
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p data/raw data/interim data/processed models reports/figures reports/metrics mlruns .dvc/cache config

# Configure Git (required by DVC) - will be overridden by env vars if provided
RUN git config --global user.email "mlops@equipo52.com" && \
    git config --global user.name "MLOps Team" && \
    git config --global --add safe.directory /app

# Create .gitignore to exclude DVC-managed files
RUN echo "/data/interim/\n/data/processed/\n/models/*.joblib\n/models/*.pkl\n/reports/figures/*.png\n/reports/figures/*.pdf\n/reports/metrics/*.json\n/mlruns/\n.dvc/cache/\n.dvc/tmp/" > .gitignore

# Initialize Git repository
RUN git init && git add -A && git commit -m "Initial commit" || echo "Git already initialized"

# Initialize DVC
RUN dvc init 2>/dev/null || echo "DVC already initialized"

# Set Python path
ENV PYTHONPATH=/app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DVC_NO_ANALYTICS=1

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

# Create entrypoint script for DVC setup
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=== Configurando DVC Remote ==="\n\
if [ ! -z "$DVC_REMOTE_URL" ] && [ ! -z "$DVC_REMOTE_NAME" ]; then\n\
  dvc remote add -d $DVC_REMOTE_NAME $DVC_REMOTE_URL -f 2>/dev/null || true\n\
  echo "DVC remote configurado: $DVC_REMOTE_NAME -> $DVC_REMOTE_URL"\n\
fi\n\
\n\
# Configurar credenciales de AWS si están presentes\n\
if [ ! -z "$AWS_ACCESS_KEY_ID" ]; then\n\
  echo "Configurando credenciales de AWS..."\n\
fi\n\
\n\
echo "=== Configuración completada ==="\n\
echo "Ejecutando comando: $@"\n\
exec "$@"\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command: ejecutar pipeline completo de DVC
CMD ["dvc", "repro"]
