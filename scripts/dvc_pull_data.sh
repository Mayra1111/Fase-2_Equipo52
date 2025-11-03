#!/bin/bash
# DVC Pull Script - Download data from S3
# Run this to get latest data from remote storage

set -e

echo "================================================"
echo "Pulling Data from DVC Remote (S3)"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env not found, using environment variables${NC}"
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check DVC status
echo "Checking DVC status..."
dvc status

# Pull data
echo ""
echo "Pulling data from S3..."
dvc pull

echo ""
echo -e "${GREEN}✓ Data pulled successfully!${NC}"
echo ""

# Show what was downloaded
echo "Downloaded files:"
ls -lh data/interim/*.csv 2>/dev/null || true
ls -lh models/*.pkl 2>/dev/null || true

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Ready to run pipelines!${NC}"
echo -e "${GREEN}================================================${NC}"
