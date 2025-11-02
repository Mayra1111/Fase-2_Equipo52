#!/bin/bash
# Script to version models with DVC

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║              DVC MODEL VERSIONING SCRIPT                          ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if DVC is initialized
if [ ! -d ".dvc" ]; then
    echo "Initializing DVC..."
    dvc init
    echo "✓ DVC initialized"
else
    echo "✓ DVC already initialized"
fi

# Add models directory to DVC tracking
if [ -d "models" ]; then
    echo ""
    echo "Adding models directory to DVC tracking..."
    
    # Check if models.dvc already exists
    if [ -f "models.dvc" ]; then
        echo "Updating models.dvc..."
        dvc add models --force
    else
        echo "Creating models.dvc..."
        dvc add models
    fi
    
    echo "✓ Models added to DVC"
    
    # Show DVC status
    echo ""
    echo "DVC Status:"
    dvc status
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║  Models versioned successfully!                                   ║"
    echo "║                                                                   ║"
    echo "║  Next steps:                                                      ║"
    echo "║    1. git add models.dvc .gitignore                               ║"
    echo "║    2. git commit -m \"Track models with DVC\"                      ║"
    echo "║    3. dvc push  (to push models to remote storage)               ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
else
    echo "✗ Models directory not found"
    echo "Run the ML pipeline first: python scripts/run_ml.py"
    exit 1
fi
