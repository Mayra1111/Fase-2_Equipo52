#!/bin/bash
# DVC Add Data Script - Track datasets with DVC
# Run this on the HOST system after dvc_setup.sh

set -e

echo "================================================"
echo "Adding Datasets to DVC"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track interim datasets
echo "Tracking interim datasets..."
if [ -f data/interim/obesity_estimation_original.csv ]; then
    dvc add data/interim/obesity_estimation_original.csv
    echo -e "${GREEN}✓ Added obesity_estimation_original.csv${NC}"
fi

if [ -f data/interim/obesity_estimation_modified.csv ]; then
    dvc add data/interim/obesity_estimation_modified.csv
    echo -e "${GREEN}✓ Added obesity_estimation_modified.csv${NC}"
fi

if [ -f data/interim/dataset_limpio.csv ]; then
    dvc add data/interim/dataset_limpio.csv
    echo -e "${GREEN}✓ Added dataset_limpio.csv${NC}"
fi

if [ -f data/interim/dataset_limpio_refactored.csv ]; then
    dvc add data/interim/dataset_limpio_refactored.csv
    echo -e "${GREEN}✓ Added dataset_limpio_refactored.csv${NC}"
fi

# Track models directory (if exists)
if [ -d models ] && [ "$(ls -A models)" ]; then
    echo ""
    echo "Tracking models directory..."
    dvc add models
    echo -e "${GREEN}✓ Added models directory${NC}"
else
    echo -e "${YELLOW}⚠ Models directory empty or doesn't exist${NC}"
fi

# Add .dvc files to Git
echo ""
echo "Adding .dvc metadata files to Git..."
git add data/interim/*.dvc models.dvc 2>/dev/null || true
git add .gitignore

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Datasets Added to DVC!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Files tracked by DVC:"
ls -lh data/interim/*.dvc 2>/dev/null || true
ls -lh models.dvc 2>/dev/null || true

echo ""
echo "Next steps:"
echo "  1. Push to S3: dvc push"
echo "  2. Commit to Git: git commit -m 'Track datasets with DVC'"
echo "  3. Push to Git: git push"
echo ""
