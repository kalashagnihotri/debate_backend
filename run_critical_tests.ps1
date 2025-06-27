# PowerShell script to run critical endpoint tests
# Online Debate Platform - Critical Test Runner

param(
    [string]$TestCategory = "all",
    [switch]$Verbose = $false,
    [switch]$KeepDb = $true,
    [switch]$Coverage = $false
)

Write-Host "Online Debate Platform - Critical Test Runner" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $venvPath

# Check if Django is available
try {
    python -c "import django; print(f'Django {django.get_version()}')" | Out-Null
    Write-Host "Django environment ready" -ForegroundColor Green
} catch {
    Write-Host "Django not available. Please install requirements:" -ForegroundColor Red
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Set environment variables
$env:DJANGO_SETTINGS_MODULE = "onlineDebatePlatform.settings"

Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host "Category: $TestCategory" -ForegroundColor Gray

# Run tests based on category
switch ($TestCategory.ToLower()) {
    "all" {
        Write-Host "Running all available tests..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints --verbosity=2 $(if ($KeepDb) { "--keepdb" } else { "" })
    }
    "auth" {
        Write-Host "Running authentication tests only..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingAuthenticationTestCase --verbosity=2 --keepdb
    }
    "validation" {
        Write-Host "Running validation tests only..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingValidationTestCase --verbosity=2 --keepdb
    }
    "performance" {
        Write-Host "Running performance tests only..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingPerformanceTestCase --verbosity=2 --keepdb
    }
    "security" {
        Write-Host "Running security tests only..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingSecurityTestCase --verbosity=2 --keepdb
    }
    "integration" {
        Write-Host "Running integration tests only..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingIntegrationTestCase --verbosity=2 --keepdb
    }
    "django" {
        Write-Host "Running Django test runner..." -ForegroundColor Cyan
        if ($Coverage) {
            Write-Host "Running with coverage..." -ForegroundColor Yellow
            coverage run --source='.' manage.py test tests.test_working_endpoints
            coverage report
            coverage html
            Write-Host "Coverage report generated in htmlcov/" -ForegroundColor Green
        } else {
            python manage.py test tests.test_working_endpoints --verbosity=2 $(if ($KeepDb) { "--keepdb" } else { "" })
        }
    }
    "pytest" {
        Write-Host "Running pytest..." -ForegroundColor Cyan
        if ($Coverage) {
            pytest tests/ --cov=. --cov-report=html --cov-report=term
        } else {
            pytest tests/ $(if ($Verbose) { "-v" } else { "" }) --tb=short
        }
    }
    "quick" {
        Write-Host "Running quick test suite..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints.WorkingAuthenticationTestCase tests.test_working_endpoints.WorkingDebateEndpointsTestCase --verbosity=1 --keepdb
    }
    "working" {
        Write-Host "Running working endpoint tests..." -ForegroundColor Cyan
        python manage.py test tests.test_working_endpoints --verbosity=2 --keepdb
    }
    default {
        Write-Host "❌ Unknown test category: $TestCategory" -ForegroundColor Red
        Write-Host ""
        Write-Host "Available categories:" -ForegroundColor Yellow
        Write-Host "  all         - Run all available tests (working + core)" -ForegroundColor Gray
        Write-Host "  working     - Run working endpoint tests only (18 tests)" -ForegroundColor Gray
        Write-Host "  auth        - Authentication tests only" -ForegroundColor Gray
        Write-Host "  validation  - API validation tests only" -ForegroundColor Gray
        Write-Host "  performance - Performance tests only" -ForegroundColor Gray
        Write-Host "  security    - Security tests only" -ForegroundColor Gray
        Write-Host "  integration - Integration tests only" -ForegroundColor Gray
        Write-Host "  django      - Use Django test runner" -ForegroundColor Gray
        Write-Host "  pytest      - Use pytest runner" -ForegroundColor Gray
        Write-Host "  quick       - Quick test suite" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Usage examples:" -ForegroundColor Yellow
        Write-Host "  .\run_critical_tests.ps1" -ForegroundColor Gray
        Write-Host "  .\run_critical_tests.ps1 -TestCategory working" -ForegroundColor Gray
        Write-Host "  .\run_critical_tests.ps1 -TestCategory auth" -ForegroundColor Gray
        Write-Host "  .\run_critical_tests.ps1 -TestCategory django -Coverage" -ForegroundColor Gray
        Write-Host "  .\run_critical_tests.ps1 -TestCategory pytest -Verbose" -ForegroundColor Gray
        exit 1
    }
}

$exitCode = $LASTEXITCODE

# Final status
Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "Tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests completed with failures." -ForegroundColor Red
    Write-Host "Please review the test output above for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  - Review any test failures above" -ForegroundColor Gray
Write-Host "  - Run specific test categories for focused testing" -ForegroundColor Gray
Write-Host "  - Generate coverage reports with -Coverage flag" -ForegroundColor Gray
Write-Host "  - Add new tests for any new features" -ForegroundColor Gray

exit $exitCode
