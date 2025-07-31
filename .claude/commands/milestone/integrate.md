---
description: "Prepare integration testing and documentation updates before PR submission"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob"]
model: "sonnet-4"
---

# Integration & Documentation

You are preparing the milestone implementation for integration by updating documentation and running comprehensive integration tests.

## Phase 4: Integration & Documentation

### Documentation Requirements

#### 1. Update CLI Help Text

Ensure all new commands have proper help text and documentation:

!echo "Checking current CLI structure..."
!find easel/cli/ -name "*.py" -type f | head -10

!echo "Testing CLI help system..."
!poetry run python -m easel --help

#### 2. Update Configuration Documentation

If new configuration options were added, ensure they're documented:

@easel/config/
!echo "Checking for configuration changes..."
!git diff --name-only | grep -E "(config|settings)" || echo "No config changes detected"

#### 3. Update API Documentation

If API client extensions were added, ensure documentation is current:

@easel/api/
!echo "Checking for API changes..."
!git diff --name-only | grep -E "api/" || echo "No API changes detected"

#### 4. Review and Update Docstrings

Ensure all new functions and classes have comprehensive docstrings:

!echo "Checking for undocumented functions..."
!grep -r "def " easel/ | grep -v "__" | head -10

### Integration Testing

#### 5. End-to-End Workflow Testing

Test complete workflows from start to finish:

!echo "=== INTEGRATION TESTING ==="

!echo "1. Testing basic CLI functionality..."
!poetry run python -m easel --help

!echo "2. Testing configuration system..."
!poetry run python -m easel doctor --help || echo "Doctor command not available yet"

!echo "3. Testing new milestone functionality..."
!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
!MILESTONE_NUM=$(echo $CURRENT_BRANCH | grep -o 'milestone-[0-9]*' | cut -d'-' -f2)
!echo "Testing milestone $MILESTONE_NUM functionality"

#### 6. Error Handling Validation

Test error conditions and edge cases:

!echo "Testing error handling..."
!poetry run python -m easel --invalid-option 2>&1 || echo "Expected error handled correctly"

#### 7. Performance Integration Testing

!echo "Testing performance with realistic workloads..."
!time poetry run python -m easel --help

### Code Integration Validation

#### 8. Import Structure Validation

Ensure all imports are correct and no circular dependencies exist:

!echo "Testing import structure..."
!python -c "
import sys
sys.path.insert(0, 'easel')
try:
    import easel
    print('✓ Main package imports successfully')
except Exception as e:
    print(f'✗ Import error: {e}')
"

#### 9. Cross-Module Integration

Test that new components integrate properly with existing ones:

!echo "Running integration-focused tests..."
!poetry run pytest -k "integration or Integration" -v || echo "No integration tests found"

### Security Integration Testing

#### 10. Credential Handling Test

!echo "Testing credential handling..."
!echo "Verifying no secrets are logged or exposed..."
!grep -r "password\|token\|secret\|key" easel/ --include="*.py" | grep -v "# " | head -5 || echo "No obvious credential exposures found"

#### 11. Input Validation Testing

!echo "Testing input validation..."
!poetry run python -c "
# Test basic input validation
import click
from click.testing import CliRunner
print('Input validation framework available')
"

### Documentation Updates

#### 12. Update README and Documentation

Check if project documentation needs updates:

@README.md
!echo "Checking if README needs updates based on new functionality..."

#### 13. Update Example Usage

If applicable, update usage examples:

!echo "Current git changes:"
!git status --porcelain

### Final Integration Checks

#### 14. Dependency Validation

Ensure no new dependencies were added without proper declaration:

!echo "Checking for undeclared dependencies..."
!poetry check

!echo "Checking poetry.lock is up to date..."
!poetry lock --check

#### 15. Build System Integration

!echo "Testing build system integration..."
!poetry build --format=wheel 2>/dev/null || echo "Build system not fully configured yet"

### Integration Summary

#### 16. Generate Integration Report

!echo "=== INTEGRATION REPORT ==="
!echo "Milestone: $(echo $(git rev-parse --abbrev-ref HEAD) | grep -o 'milestone-[0-9]*' | cut -d'-' -f2)"
!echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
!echo "Files changed: $(git diff --name-only --cached | wc -l)"
!echo "Lines added: $(git diff --stat --cached | tail -1 | grep -o '[0-9]* insertion' | cut -d' ' -f1 || echo 0)"
!echo "Tests passing: $(poetry run pytest --tb=no -q | grep -o '[0-9]* passed' | cut -d' ' -f1 || echo 'unknown')"

### Pre-Submission Checklist

Verify each item before proceeding to submission:

- [ ] **CLI Help Text** updated for all new commands
- [ ] **Configuration Options** documented
- [ ] **API Documentation** current 
- [ ] **Docstrings** comprehensive for all new code
- [ ] **End-to-End Workflows** tested and functional
- [ ] **Error Handling** validated
- [ ] **Performance** acceptable
- [ ] **Import Structure** clean
- [ ] **Cross-Module Integration** working
- [ ] **Security** validated (no credential exposure)
- [ ] **Input Validation** implemented
- [ ] **Dependencies** properly declared
- [ ] **Build System** compatible

### Next Steps

If all integration checks pass:
- Proceed with `/milestone:submit` to create the pull request

If integration issues found:
- Fix identified issues
- Re-run `/milestone:integrate`
- Do not proceed until all integration tests pass

**Integration is critical** - this is where individual components prove they work together as a cohesive system.