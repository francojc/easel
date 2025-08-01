---
description: "Prepare release artifacts and distribution packages for Easel CLI"
allowed-tools: ["Bash", "Read", "Write"]
---

# Easel CLI Release Preparation

Prepare and validate release artifacts for Easel CLI distribution.

## Pre-Release Validation

### Version Information
!poetry version
!git describe --tags --always
!echo "Current branch: $(git branch --show-current)"

### Quality Gate Validation
!echo "=== PRE-RELEASE QUALITY GATES ==="

### Test Suite Validation
!poetry run pytest --tb=no -q
!echo "Tests: $?"

### Coverage Validation
!poetry run coverage report --fail-under=80 > /dev/null 2>&1 && echo "✓ Coverage: PASS (≥80%)" || echo "✗ Coverage: FAIL (<80%)"

### Security Validation
!poetry run bandit -r easel/ -q && echo "✓ Security: PASS" || echo "✗ Security: FAIL"
!poetry run safety check --json > /dev/null 2>&1 && echo "✓ Dependencies: SECURE" || echo "✗ Dependencies: VULNERABLE"

### Code Quality Validation
!poetry run black --check easel/ tests/ > /dev/null 2>&1 && echo "✓ Formatting: PASS" || echo "✗ Formatting: FAIL"
!poetry run flake8 easel/ tests/ > /dev/null 2>&1 && echo "✓ Linting: PASS" || echo "✗ Linting: FAIL"
!poetry run mypy easel/ > /dev/null 2>&1 && echo "✓ Type Check: PASS" || echo "✗ Type Check: FAIL"

## Build Preparation

### Clean Previous Builds
!rm -rf dist/ build/ *.egg-info/
!echo "Cleaned previous build artifacts"

### Build Source Distribution
!poetry build -f sdist
!echo "Source distribution built"

### Build Wheel Distribution
!poetry build -f wheel
!echo "Wheel distribution built"

### Validate Build Artifacts
!ls -la dist/
!echo ""
!echo "Build artifact validation:"
!for file in dist/*; do
    echo "✓ $(basename "$file"): $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown") bytes"
done

## Distribution Validation

### Test Installation from Build
!echo "=== TESTING INSTALLATION FROM BUILD ==="
!pip install --user --force-reinstall dist/*.whl
!echo "Wheel installation test: $?"

### Validate CLI Entry Point
!easel --version 2>/dev/null && echo "✓ CLI entry point: WORKING" || echo "✗ CLI entry point: FAILED"
!easel --help > /dev/null 2>&1 && echo "✓ CLI help: WORKING" || echo "✗ CLI help: FAILED"

### Test Basic Commands
!easel doctor > /dev/null 2>&1 && echo "✓ Doctor command: WORKING" || echo "✗ Doctor command: FAILED"

## Release Notes Generation

### Generate Changelog Since Last Tag
!echo "=== CHANGELOG SINCE LAST RELEASE ==="
!git log $(git describe --tags --abbrev=0)..HEAD --oneline --pretty=format:"- %s (%h)" || git log --oneline -10 --pretty=format:"- %s (%h)"

### Git Status Check
!echo ""
!echo "=== GIT STATUS CHECK ==="
!git status --porcelain | wc -l | xargs echo "Uncommitted changes:"
!git status --porcelain

## Release Checklist

!echo ""
!echo "=== RELEASE READINESS CHECKLIST ==="
!echo ""
!echo "Pre-Release Requirements:"
!poetry run pytest --tb=no -q > /dev/null 2>&1 && echo "✓ All tests passing" || echo "✗ Tests failing"
!poetry run coverage report --fail-under=80 > /dev/null 2>&1 && echo "✓ Coverage ≥80%" || echo "✗ Coverage <80%"
!poetry run bandit -r easel/ -q && echo "✓ Security scan clean" || echo "✗ Security issues found"
!git status --porcelain | [ $(wc -l) -eq 0 ] && echo "✓ Working directory clean" || echo "✗ Uncommitted changes"
![ -f "CHANGELOG.md" ] && echo "✓ Changelog present" || echo "? Changelog missing (optional)"
![ -f "README.md" ] && echo "✓ README present" || echo "✗ README missing"

!echo ""
!echo "Build Artifacts:"
![ -d "dist" ] && echo "✓ Distribution directory exists" || echo "✗ No distribution built"
!ls dist/*.whl > /dev/null 2>&1 && echo "✓ Wheel package built" || echo "✗ No wheel package"
!ls dist/*.tar.gz > /dev/null 2>&1 && echo "✓ Source package built" || echo "✗ No source package"

!echo ""
!echo "Next Steps:"
!echo "1. Review and test the built packages in dist/"
!echo "2. Create and push a git tag: git tag v$(poetry version -s) && git push origin v$(poetry version -s)"
!echo "3. Publish to PyPI: poetry publish (requires authentication)"
!echo "4. Create GitHub release with changelog"
!echo "5. Update documentation with new version"

!echo ""
!echo "Release preparation complete. Review all checklist items before publishing."