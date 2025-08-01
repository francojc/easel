---
description: "Run comprehensive test suite with coverage reporting and quality checks for Easel CLI"
allowed-tools: ["Bash", "Read"]
---

# Easel CLI Test Suite Runner

Run comprehensive testing and quality validation for the Easel CLI project.

## Test Execution

### Unit and Integration Tests
!poetry run pytest -v --tb=short --cov=easel --cov-report=term-missing --cov-report=html

### Coverage Summary
!poetry run coverage report --show-missing

### Test Results Analysis
Review test results and coverage:

@htmlcov/index.html

## Quality Checks

### Code Formatting
!poetry run black --check easel/ tests/

### Linting
!poetry run flake8 easel/ tests/

### Type Checking
!poetry run mypy easel/

### Security Scanning
!poetry run bandit -r easel/
!poetry run safety check

## Pre-commit Validation
!poetry run pre-commit run --all-files

## Test Environment Validation

Verify test environment is properly configured:

!poetry run python -c "import easel; print(f'Easel package loaded from: {easel.__file__}')"
!poetry run pytest --version
!poetry run coverage --version

## Test Results Summary

Generate comprehensive test report:

!echo "=== EASEL CLI TEST SUMMARY ==="
!echo "Date: $(date)"
!echo "Git commit: $(git rev-parse --short HEAD)"
!echo "Git branch: $(git branch --show-current)"
!echo ""
!echo "Test Coverage:"
!poetry run coverage report --skip-covered | tail -n 1
!echo ""
!echo "Quality Status:"
!poetry run black --check easel/ tests/ > /dev/null 2>&1 && echo "✓ Code formatting: PASS" || echo "✗ Code formatting: FAIL"
!poetry run flake8 easel/ tests/ > /dev/null 2>&1 && echo "✓ Code linting: PASS" || echo "✗ Code linting: FAIL"
!poetry run mypy easel/ > /dev/null 2>&1 && echo "✓ Type checking: PASS" || echo "✗ Type checking: FAIL"
!poetry run bandit -r easel/ > /dev/null 2>&1 && echo "✓ Security scan: PASS" || echo "✗ Security scan: FAIL"

All tests and quality checks completed. Review the results above and address any failing checks before proceeding with development.
