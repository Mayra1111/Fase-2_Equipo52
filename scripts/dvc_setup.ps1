# DVC Setup Script for Windows PowerShell
# Run this ONCE on the HOST system (not in Docker)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "DVC Setup for Obesity ML Project (Windows)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env from .env.example and configure AWS credentials"
    Write-Host "  Copy-Item .env.example .env"
    exit 1
}

# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$name" -Value $value
    }
}

# Check if DVC is installed
try {
    dvc version | Out-Null
    Write-Host "✓ DVC already installed" -ForegroundColor Green
} catch {
    Write-Host "DVC not installed!" -ForegroundColor Red
    Write-Host "Installing DVC with S3 support..."
    pip install "dvc[s3]"
}

# Check if Git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Error: Not a Git repository!" -ForegroundColor Red
    Write-Host "Please initialize Git first: git init"
    exit 1
}

# Initialize DVC
if (-not (Test-Path .dvc)) {
    Write-Host "Initializing DVC..."
    dvc init
    Write-Host "✓ DVC initialized" -ForegroundColor Green
} else {
    Write-Host "⚠ DVC already initialized" -ForegroundColor Yellow
}

# Configure S3 remote
Write-Host ""
Write-Host "Configuring S3 remote storage..."
try {
    dvc remote add -d $env:DVC_REMOTE_NAME $env:DVC_REMOTE_URL 2>&1 | Out-Null
} catch {
    Write-Host "⚠ Remote already exists" -ForegroundColor Yellow
}

# Configure AWS credentials
dvc remote modify $env:DVC_REMOTE_NAME access_key_id $env:AWS_ACCESS_KEY_ID
dvc remote modify $env:DVC_REMOTE_NAME secret_access_key $env:AWS_SECRET_ACCESS_KEY
dvc remote modify $env:DVC_REMOTE_NAME region $env:AWS_DEFAULT_REGION

Write-Host "✓ S3 remote configured" -ForegroundColor Green

# Verify configuration
Write-Host ""
Write-Host "DVC Configuration:"
Write-Host "=================="
dvc remote list
Write-Host ""
dvc config core.remote

# Test S3 connection
Write-Host ""
Write-Host "Testing S3 connection..."
try {
    aws s3 ls "s3://$env:AWS_S3_BUCKET/" | Out-Null
    Write-Host "✓ S3 connection successful" -ForegroundColor Green
} catch {
    Write-Host "✗ S3 connection failed" -ForegroundColor Red
    Write-Host "Please verify AWS credentials and bucket name"
}

# Add .dvc files to Git
Write-Host ""
Write-Host "Adding DVC configuration to Git..."
git add .dvc/.gitignore .dvc/config

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "DVC Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Add datasets to DVC: .\scripts\dvc_add_data.ps1"
Write-Host "  2. Push to S3: dvc push"
Write-Host "  3. Commit changes: git commit -m 'Initialize DVC'"
Write-Host ""
