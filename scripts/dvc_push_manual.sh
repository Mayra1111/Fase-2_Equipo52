#!/bin/bash
# Script alternativo para subir archivos versionados por DVC a S3
# Usa AWS CLI directamente para evitar problemas de permisos con boto3

set -e

echo "========================================"
echo "DVC MANUAL PUSH - Subida a S3"
echo "========================================"
echo ""

# Configuración
S3_BUCKET="${AWS_S3_BUCKET:-itesm-mna}"
S3_PREFIX="202502-equipo52/dvc-storage"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📦 Bucket: s3://${S3_BUCKET}/${S3_PREFIX}"
echo "🕒 Timestamp: ${TIMESTAMP}"
echo ""

# Función para subir archivo si existe
upload_if_exists() {
    local file=$1
    local s3_path=$2
    
    if [ -f "$file" ]; then
        echo "⬆️  Subiendo: $file"
        aws s3 cp "$file" "s3://${S3_BUCKET}/${S3_PREFIX}/${s3_path}" \
            --region ${AWS_DEFAULT_REGION:-us-east-1} \
            --metadata "uploaded=${TIMESTAMP},pipeline=dvc"
        echo "   ✅ Completado: s3://${S3_BUCKET}/${S3_PREFIX}/${s3_path}"
    else
        echo "   ⚠️  No encontrado: $file"
    fi
}

echo "=== Subiendo Dataset ==="
upload_if_exists "data/interim/dataset_limpio_refactored.csv" "data/dataset_limpio_refactored.csv"
echo ""

echo "=== Subiendo Modelos ==="
upload_if_exists "models/best_pipeline.joblib" "models/best_pipeline.joblib"
upload_if_exists "models/model_metadata.joblib" "models/model_metadata.joblib"
echo ""

echo "=== Subiendo Métricas ==="
upload_if_exists "reports/metrics/evaluation_metrics.json" "metrics/evaluation_metrics.json"
echo ""

echo "=== Subiendo Visualizaciones ==="
if [ -d "reports/figures" ]; then
    echo "⬆️  Subiendo visualizaciones..."
    aws s3 sync reports/figures/ "s3://${S3_BUCKET}/${S3_PREFIX}/figures/" \
        --region ${AWS_DEFAULT_REGION:-us-east-1} \
        --exclude "*.md" \
        --exclude "*.txt"
    echo "   ✅ Visualizaciones sincronizadas"
fi
echo ""

# Guardar manifiesto
echo "=== Creando Manifiesto ==="
MANIFEST_FILE="/tmp/dvc_manifest_${TIMESTAMP}.json"
cat > "$MANIFEST_FILE" << EOF
{
  "timestamp": "${TIMESTAMP}",
  "pipeline": "dvc-manual-push",
  "files": [
    {"path": "data/dataset_limpio_refactored.csv", "size": $(stat -c%s data/interim/dataset_limpio_refactored.csv 2>/dev/null || echo 0)},
    {"path": "models/best_pipeline.joblib", "size": $(stat -c%s models/best_pipeline.joblib 2>/dev/null || echo 0)},
    {"path": "models/model_metadata.joblib", "size": $(stat -c%s models/model_metadata.joblib 2>/dev/null || echo 0)}
  ]
}
EOF

aws s3 cp "$MANIFEST_FILE" "s3://${S3_BUCKET}/${S3_PREFIX}/manifests/manifest_${TIMESTAMP}.json" \
    --region ${AWS_DEFAULT_REGION:-us-east-1}
echo "   ✅ Manifiesto guardado: s3://${S3_BUCKET}/${S3_PREFIX}/manifests/manifest_${TIMESTAMP}.json"
echo ""

echo "========================================"
echo "✅ PUSH COMPLETADO EXITOSAMENTE"
echo "========================================"
echo ""
echo "🔗 Para verificar archivos:"
echo "   aws s3 ls s3://${S3_BUCKET}/${S3_PREFIX}/ --recursive"
