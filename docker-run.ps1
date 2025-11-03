# PowerShell script to run the Obesity ML Project with Docker

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Function to show usage
function Show-Usage {
    Write-Host @"
===============================================================================
                                                                              
            OBESITY ML PROJECT - DOCKER HELPER                               
                                                                              
===============================================================================

USAGE:
    .\docker-run.ps1 [COMMAND]

COMMANDS:

  PIPELINE COMMANDS:
    eda           Run the EDA pipeline (data cleaning)
    ml            Run the ML pipeline (model training)
    visualize     Generate EDA visualizations (PNG images)
    compare       Compare datasets (validate results)
    test          Run unit tests
    all           Run EDA + ML + Visualize + Compare + Test (complete workflow)

  SERVER COMMANDS:
    mlflow        Start MLflow UI (http://localhost:5000)
    shell         Open interactive bash shell inside container

  MANAGEMENT COMMANDS:
    build         Build Docker images
    clean         Remove all containers and images
    logs          Show logs from running containers
    stop          Stop all running containers

  HELP:
    help          Show this help message

EXAMPLES:

  # Run complete workflow (recommended for first time)
  .\docker-run.ps1 all

  # Run only EDA pipeline
  .\docker-run.ps1 eda

  # Run ML training
  .\docker-run.ps1 ml

  # Generate visualizations
  .\docker-run.ps1 visualize

  # Compare results
  .\docker-run.ps1 compare

  # Run tests
  .\docker-run.ps1 test

"@
}

# Execute based on command
switch ($Command.ToLower()) {
    "eda" {
        Write-Host "Running EDA pipeline..." -ForegroundColor Blue
        docker-compose run --rm eda-pipeline
        if ($LASTEXITCODE -eq 0) {
            Write-Host "EDA pipeline complete!" -ForegroundColor Green
        }
    }
    "ml" {
        Write-Host "Running ML pipeline..." -ForegroundColor Blue
        docker-compose run --rm ml-pipeline
        if ($LASTEXITCODE -eq 0) {
            Write-Host "ML pipeline complete!" -ForegroundColor Green
        }
    }
    "visualize" {
        Write-Host "Generating EDA visualizations..." -ForegroundColor Blue
        docker-compose run --rm visualize
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Visualizations generated in reports/figures/" -ForegroundColor Green
        }
    }
    "compare" {
        Write-Host "Comparing datasets..." -ForegroundColor Blue
        docker-compose run --rm compare
    }
    "test" {
        Write-Host "Running tests..." -ForegroundColor Blue
        docker-compose run --rm test
    }
    "all" {
        Write-Host "Running complete workflow..." -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Step 1/5: Running EDA pipeline..." -ForegroundColor Blue
        docker-compose run --rm eda-pipeline
        if ($LASTEXITCODE -eq 0) {
            Write-Host "EDA pipeline complete!" -ForegroundColor Green
        }
        Write-Host ""
        
        Write-Host "Step 2/5: Running ML pipeline..." -ForegroundColor Blue
        docker-compose run --rm ml-pipeline
        if ($LASTEXITCODE -eq 0) {
            Write-Host "ML pipeline complete!" -ForegroundColor Green
        }
        Write-Host ""
        
        Write-Host "Step 3/5: Generating visualizations..." -ForegroundColor Blue
        docker-compose run --rm visualize
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Visualizations generated!" -ForegroundColor Green
        }
        Write-Host ""
        
        Write-Host "Step 4/5: Comparing datasets..." -ForegroundColor Blue
        docker-compose run --rm compare
        Write-Host ""
        
        Write-Host "Step 5/5: Running tests..." -ForegroundColor Blue
        docker-compose run --rm test
        Write-Host ""
        
        Write-Host "===============================================================================" -ForegroundColor Green
        Write-Host "                                                                               " -ForegroundColor Green
        Write-Host "              COMPLETE WORKFLOW FINISHED!                                      " -ForegroundColor Green
        Write-Host "                                                                               " -ForegroundColor Green
        Write-Host "===============================================================================" -ForegroundColor Green
    }
    "mlflow" {
        Write-Host "Starting MLflow UI..." -ForegroundColor Blue
        Write-Host "Access MLflow at: http://localhost:5000" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        docker-compose up mlflow
    }
    "shell" {
        Write-Host "Opening interactive shell..." -ForegroundColor Blue
        Write-Host "Type 'exit' to leave the shell" -ForegroundColor Yellow
        docker-compose run --rm shell bash
    }
    "build" {
        Write-Host "Building Docker images..." -ForegroundColor Blue
        docker-compose build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build complete!" -ForegroundColor Green
        }
    }
    "logs" {
        Write-Host "Showing logs..." -ForegroundColor Blue
        docker-compose logs --tail=100 -f
    }
    "stop" {
        Write-Host "Stopping all containers..." -ForegroundColor Blue
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "All containers stopped!" -ForegroundColor Green
        }
    }
    "clean" {
        Write-Host "Cleaning all containers and images..." -ForegroundColor Yellow
        docker-compose down --rmi all --volumes --remove-orphans
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Cleanup complete!" -ForegroundColor Green
        }
    }
    "help" {
        Show-Usage
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Usage
        exit 1
    }
}




