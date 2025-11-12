#!/bin/bash
set -e

echo "========================================"
echo "DVC FULL PIPELINE - Pipeline + Push"
echo "========================================"
echo ""

# Step 1: Execute the pipeline
echo "> Step 1: Running DVC pipeline..."
echo ""
dvc status
echo ""
echo "> Executing dvc repro..."
dvc repro --verbose
echo ""
echo "✓ Pipeline completed successfully!"
echo ""

# Step 2: Push to remote
echo "> Step 2: Pushing to remote storage..."
dvc push --verbose
echo ""
echo "✓ Push completed successfully!"
echo ""

# Summary
echo "========================================"
echo "✓ Pipeline executed and pushed successfully!"
echo "========================================"
