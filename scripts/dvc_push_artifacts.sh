#!/bin/bash
# DVC Push Script - Upload data/models to S3
# Run this after training new models or updating datasets

set -e

echo "================================================"
echo "Pushing Artifacts to DVC Remote (S3)"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check what will be pushed
echo "Checking DVC status..."
dvc status

# Ask for confirmation
echo ""
read -p "Do you want to push changes to S3? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled"
    exit 0
fi

# Push to S3
echo ""
echo "Pushing to S3..."
dvc push

echo ""
echo -e "${GREEN}✓ Artifacts pushed successfully!${NC}"
echo ""

# Remind to commit .dvc files
echo -e "${YELLOW}Don't forget to commit .dvc files to Git:${NC}"
echo "  git add data/interim/*.dvc models.dvc"
echo "  git commit -m 'Update DVC tracked files'"
echo "  git push"
echo ""
