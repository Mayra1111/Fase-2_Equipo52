#!/bin/bash
# DVC Setup Script - Initial Configuration
# Run this ONCE on the HOST system (not in Docker)

set -e  # Exit on error

echo "================================================"
echo "DVC Setup for Obesity ML Project"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env from .env.example and configure AWS credentials"
    echo "  cp .env.example .env"
    exit 1
fi

# Load environment variables
echo "Loading environment variables from .env..."
export $(cat .env | grep -v '^#' | xargs)

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo -e "${RED}DVC not installed!${NC}"
    echo "Installing DVC with S3 support..."
    pip install 'dvc[s3]'
else
    echo -e "${GREEN}✓ DVC already installed${NC}"
fi

# Check if Git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}Error: Not a Git repository!${NC}"
    echo "Please initialize Git first: git init"
    exit 1
fi

# Initialize DVC
if [ ! -d .dvc ]; then
    echo "Initializing DVC..."
    dvc init
    echo -e "${GREEN}✓ DVC initialized${NC}"
else
    echo -e "${YELLOW}⚠ DVC already initialized${NC}"
fi

# Configure S3 remote
echo ""
echo "Configuring S3 remote storage..."
dvc remote add -d ${DVC_REMOTE_NAME} ${DVC_REMOTE_URL} 2>/dev/null || \
    echo -e "${YELLOW}⚠ Remote already exists${NC}"

# Configure AWS credentials
dvc remote modify ${DVC_REMOTE_NAME} access_key_id ${AWS_ACCESS_KEY_ID}
dvc remote modify ${DVC_REMOTE_NAME} secret_access_key ${AWS_SECRET_ACCESS_KEY}
dvc remote modify ${DVC_REMOTE_NAME} region ${AWS_DEFAULT_REGION}

echo -e "${GREEN}✓ S3 remote configured${NC}"

# Verify configuration
echo ""
echo "DVC Configuration:"
echo "=================="
dvc remote list
echo ""
dvc config core.remote

# Test S3 connection
echo ""
echo "Testing S3 connection..."
if aws s3 ls s3://${AWS_S3_BUCKET}/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ S3 connection successful${NC}"
else
    echo -e "${RED}✗ S3 connection failed${NC}"
    echo "Please verify AWS credentials and bucket name"
fi

# Add .dvc files to Git
echo ""
echo "Adding DVC configuration to Git..."
git add .dvc/.gitignore .dvc/config

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}DVC Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Add datasets to DVC: ./scripts/dvc_add_data.sh"
echo "  2. Push to S3: dvc push"
echo "  3. Commit changes: git commit -m 'Initialize DVC'"
echo ""
