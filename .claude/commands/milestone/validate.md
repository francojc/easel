---
description: "Run comprehensive quality assurance validation including tests, coverage, and acceptance criteria"
allowed-tools: ["Bash", "Read"]
---

# Quality Assurance Protocol

You are validating the milestone implementation against all quality requirements before integration.

## Phase 3: Quality Assurance Protocol

### Testing Requirements

#### 1. Run Comprehensive Test Suite

Execute the full test suite with coverage reporting:

!poetry run pytest --cov=easel --cov-report=term-missing --cov-report=html -v

#### 2. Coverage Validation

Check that coverage meets milestone requirements:

!echo "Coverage Requirements:"
!echo "- Regular milestones: >80% coverage"
!echo "- Production milestone: >95% coverage"
!echo ""
!echo "Current coverage:"
!poetry run coverage report --show-missing

#### 3. Individual Test Categories

Run specific test categories to ensure comprehensive validation:

!echo "Running unit tests..."
!poetry run pytest tests/unit/ -v || echo "No unit tests directory found"

!echo "Running integration tests..."  
!poetry run pytest tests/integration/ -v || echo "No integration tests directory found"

!echo "Running CLI tests..."
!poetry run pytest tests/cli/ -v || echo "No CLI tests directory found"

### Code Quality Validation

#### 4. Code Formatting

!echo "Checking code formatting..."
!poetry run black easel/ tests/ --check --diff

!echo "Applying formatting if needed..."
!poetry run black easel/ tests/

#### 5. Linting

!echo "Running flake8 linting..."
!poetry run flake8 easel/ tests/

#### 6. Type Checking

!echo "Running mypy type checking..."
!poetry run mypy easel/

#### 7. Pre-commit Hooks

!echo "Running all pre-commit hooks..."
!poetry run pre-commit run --all-files

### Security Validation

#### 8. Security Scan

!echo "Checking for common security issues..."
!poetry run bandit -r easel/ || echo "Bandit not configured - install with: poetry add --group dev bandit"

#### 9. Dependency Security Check

!echo "Checking dependencies for known vulnerabilities..."
!poetry run safety check || echo "Safety not configured - install with: poetry add --group dev safety"

### Acceptance Criteria Validation

#### 10. Review Milestone Specification

Read the current milestone specification to verify all acceptance criteria:

!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
!MILESTONE_NUM=$(echo $CURRENT_BRANCH | grep -o 'milestone-[0-9]*' | cut -d'-' -f2)
!echo "Validating milestone $MILESTONE_NUM acceptance criteria:"
@specs/$MILESTONE_NUM-*.md

### Manual Validation

#### 11. End-to-End Testing

Test the complete workflows manually:

!echo "Testing CLI functionality..."
!poetry run python -m easel --help

!echo "Testing configuration..."
!poetry run python -m easel init --help || echo "Init command not yet implemented"

!echo "Testing new functionality..."
!echo "Test the newly implemented commands manually to ensure they work as expected"

### Performance Validation

#### 12. Basic Performance Check

!echo "Running basic performance validation..."
!time poetry run python -m easel --help

### Documentation Validation

#### 13. Help Text Validation

!echo "Validating CLI help text..."
!poetry run python -m easel --help
!echo ""
!echo "Checking command-specific help:"
!poetry run python -m easel --help | grep -o '^  [a-z-]*' | while read cmd; do
  echo "Help for: $cmd"
  poetry run python -m easel $cmd --help 2>/dev/null || echo "No help available for $cmd"
done

## Validation Results Summary

### Quality Metrics Summary

!echo "=== VALIDATION SUMMARY ==="
!echo "1. Test Coverage: $(poetry run coverage report | grep TOTAL | awk '{print $4}')"
!echo "2. Code Quality: $(poetry run flake8 easel/ tests/ --count) flake8 issues"
!echo "3. Type Safety: $(poetry run mypy easel/ | grep -c error || echo 0) mypy errors"
!echo "4. Security: Bandit and Safety scans completed"
!echo "5. Pre-commit: All hooks validated"

### Pre-Integration Checklist

Mark each item as you verify:

- [ ] **Test Coverage** ≥ 80% (or ≥ 95% for production milestone)
- [ ] **All Tests Pass** consistently
- [ ] **Code Quality** checks pass (black, flake8, mypy)
- [ ] **Security Scans** complete without critical issues
- [ ] **Pre-commit Hooks** pass
- [ ] **Acceptance Criteria** manually validated
- [ ] **CLI Help Text** updated and accurate
- [ ] **End-to-End Workflows** functional
- [ ] **Performance** acceptable
- [ ] **Documentation** updated

### Next Steps

If all validations pass:
- Proceed with `/milestone:integrate` to prepare documentation and integration

If validations fail:
- Fix identified issues
- Re-run `/milestone:validate`
- Do not proceed until all issues are resolved

**Remember:** Do not proceed to integration until ALL validation criteria pass. Production code for educational institutions requires zero compromises on quality.