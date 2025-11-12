#!/bin/bash
# Script para descargar archivos desde S3 (DVC Pull alternativo)

set -e

echo "========================================"
echo "DVC MANUAL PULL - Descarga desde S3"
echo "========================================"
echo ""

# Configuración
S3_BUCKET="${AWS_S3_BUCKET:-itesm-mna}"
S3_PREFIX="202502-equipo52/dvc-storage"

echo "📦 Bucket: s3://${S3_BUCKET}/${S3_PREFIX}"
echo ""

# Función para descargar archivo si existe en S3
download_if_exists() {
    local s3_path=$1
    local local_path=$2
    
    echo "⬇️  Descargando: $s3_path"
    if aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/${s3_path}" --region ${AWS_DEFAULT_REGION:-us-east-1} > /dev/null 2>&1; then
        mkdir -p "$(dirname "$local_path")"
        aws s3 cp "s3://${S3_BUCKET}/${S3_PREFIX}/${s3_path}" "$local_path" \
            --region ${AWS_DEFAULT_REGION:-us-east-1}
        echo "   ✅ Descargado: $local_path"
    else
        echo "   ⚠️  No encontrado en S3: $s3_path"
    fi
}

echo "=== Descargando Dataset ==="
download_if_exists "data/dataset_limpio_refactored.csv" "data/interim/dataset_limpio_refactored.csv"
echo ""

echo "=== Descargando Modelos ==="
download_if_exists "models/best_pipeline.joblib" "models/best_pipeline.joblib"
download_if_exists "models/model_metadata.joblib" "models/model_metadata.joblib"
echo ""

echo "=== Descargando Métricas ==="
download_if_exists "metrics/evaluation_metrics.json" "reports/metrics/evaluation_metrics.json"
echo ""

echo "=== Descargando Visualizaciones ==="
if aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/figures/" --region ${AWS_DEFAULT_REGION:-us-east-1} > /dev/null 2>&1; then
    echo "⬇️  Descargando visualizaciones..."
    mkdir -p reports/figures
    aws s3 sync "s3://${S3_BUCKET}/${S3_PREFIX}/figures/" reports/figures/ \
        --region ${AWS_DEFAULT_REGION:-us-east-1}
    echo "   ✅ Visualizaciones descargadas"
else
    echo "   ⚠️  No hay visualizaciones en S3"
fi
echo ""

echo "========================================"
echo "✅ PULL COMPLETADO EXITOSAMENTE"
echo "========================================"
