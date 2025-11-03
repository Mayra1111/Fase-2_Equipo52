# DVC Add Data Script for Windows PowerShell
# Track datasets with DVC

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Adding Datasets to DVC" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Track interim datasets
Write-Host "Tracking interim datasets..."

if (Test-Path data/interim/obesity_estimation_original.csv) {
    dvc add data/interim/obesity_estimation_original.csv
    Write-Host "✓ Added obesity_estimation_original.csv" -ForegroundColor Green
}

if (Test-Path data/interim/obesity_estimation_modified.csv) {
    dvc add data/interim/obesity_estimation_modified.csv
    Write-Host "✓ Added obesity_estimation_modified.csv" -ForegroundColor Green
}

if (Test-Path data/interim/dataset_limpio.csv) {
    dvc add data/interim/dataset_limpio.csv
    Write-Host "✓ Added dataset_limpio.csv" -ForegroundColor Green
}

if (Test-Path data/interim/dataset_limpio_refactored.csv) {
    dvc add data/interim/dataset_limpio_refactored.csv
    Write-Host "✓ Added dataset_limpio_refactored.csv" -ForegroundColor Green
}

# Track models directory (if exists)
if ((Test-Path models) -and ((Get-ChildItem models).Count -gt 0)) {
    Write-Host ""
    Write-Host "Tracking models directory..."
    dvc add models
    Write-Host "✓ Added models directory" -ForegroundColor Green
} else {
    Write-Host "⚠ Models directory empty or doesn't exist" -ForegroundColor Yellow
}

# Add .dvc files to Git
Write-Host ""
Write-Host "Adding .dvc metadata files to Git..."
git add data/interim/*.dvc 2>$null
git add models.dvc 2>$null
git add .gitignore

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Datasets Added to DVC!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files tracked by DVC:"
Get-ChildItem data/interim/*.dvc | Format-Table Name, Length

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Push to S3: dvc push"
Write-Host "  2. Commit to Git: git commit -m 'Track datasets with DVC'"
Write-Host "  3. Push to Git: git push"
Write-Host ""
