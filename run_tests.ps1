# PowerShell script to run Django tests
# Run all tests for the Online Debate Platform

Write-Host "Starting Django Test Suite..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Warning: Virtual environment not detected. Attempting to activate..." -ForegroundColor Yellow
    
    # Try to activate virtual environment
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        & .\.venv\Scripts\Activate.ps1
        Write-Host "Virtual environment activated." -ForegroundColor Green
    } else {
        Write-Host "Virtual environment not found. Please activate manually." -ForegroundColor Red
        exit 1
    }
}

# Set test settings
$env:DJANGO_SETTINGS_MODULE = "onlineDebatePlatform.test_settings"

Write-Host "Running tests with test settings..." -ForegroundColor Cyan

# Run tests with coverage if available
try {
    # Check if coverage is available
    coverage --version | Out-Null
    Write-Host "Running tests with coverage..." -ForegroundColor Cyan
    
    # Run tests with coverage
    coverage run --source='.' manage.py test users.tests debates.tests notifications.tests tests --verbosity=2
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nTests completed successfully!" -ForegroundColor Green
        Write-Host "Generating coverage report..." -ForegroundColor Cyan
        coverage report
        coverage html
        Write-Host "`nCoverage report generated in htmlcov/ directory" -ForegroundColor Green
    } else {
        Write-Host "`nSome tests failed!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "Coverage not available. Running tests without coverage..." -ForegroundColor Yellow
    
    # Run tests without coverage
    python manage.py test users.tests debates.tests notifications.tests tests --verbosity=2
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nTests completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`nSome tests failed!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "`nTest suite completed." -ForegroundColor Green
