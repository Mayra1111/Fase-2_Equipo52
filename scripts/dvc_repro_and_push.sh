#!/bin/bash
set -e

echo "========================================"
echo "DVC PIPELINE + PUSH TO REMOTE"
echo "========================================"

echo ""
echo "Step 1: Running DVC Pipeline..."
dvc repro --verbose

echo ""
echo "Step 2: Pushing to remote storage..."
dvc push --verbose

echo ""
echo "========================================"
echo "✓ Pipeline executed and pushed successfully!"
echo "========================================"
