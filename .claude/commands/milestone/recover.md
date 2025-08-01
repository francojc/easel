---
description: "Error handling and recovery protocols for milestone development failures"
argument-hint: "<phase>"
allowed-tools: ["Bash", "Read", "Write", "Edit"]
---

# Milestone Development Recovery

You are executing recovery protocols for milestone development failures. The phase argument should be one of: setup, analyze, implement, validate, integrate, submit.

## Recovery Protocol for Phase: $ARGUMENTS

### Common Failure Scenarios

#### 1. Identify Failure Context

!echo "=== RECOVERY ANALYSIS FOR PHASE: $ARGUMENTS ==="
!echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
!echo "Git status:"
!git status --porcelain
!echo ""
!echo "Recent commits:"
!git log --oneline -3

### Phase-Specific Recovery Procedures

#### Setup Phase Recovery

!if [ "$ARGUMENTS" = "setup" ]; then
  echo "=== SETUP PHASE RECOVERY ==="
  
  echo "1. Checking Python environment..."
  python --version || echo "❌ Python installation issue"
  
  echo "2. Checking Poetry installation..."
  poetry --version || echo "❌ Poetry installation issue - run: curl -sSL https://install.python-poetry.org | python3 -"
  
  echo "3. Reinstalling dependencies..."
  poetry install --with dev || echo "❌ Dependency installation failed"
  
  echo "4. Reinitializing pre-commit..."
  poetry run pre-commit install || echo "❌ Pre-commit setup failed"
  
  echo "Setup recovery complete. Re-run /milestone:setup to verify."
fi

#### Analyze Phase Recovery

!if [ "$ARGUMENTS" = "analyze" ]; then
  echo "=== ANALYZE PHASE RECOVERY ==="
  
  echo "1. Checking GitHub CLI authentication..."
  gh auth status || echo "❌ GitHub CLI not authenticated - run: gh auth login"
  
  echo "2. Checking for existing issues..."
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ $CURRENT_BRANCH =~ issue-([0-9]+) ]]; then
    ISSUE_NUM=${BASH_REMATCH[1]}
    echo "Found existing issue: #$ISSUE_NUM"
    gh issue view $ISSUE_NUM || echo "Issue may be invalid"
  fi
  
  echo "3. Checking milestone specifications..."
  ls specs/*.md | head -5
  
  echo "4. Branch cleanup if needed..."
  echo "Current branch: $CURRENT_BRANCH"
  if [[ $CURRENT_BRANCH =~ feature/ ]]; then
    echo "On feature branch - recovery may require branch reset"
    echo "Consider: git checkout main && git branch -D $CURRENT_BRANCH"
  fi
  
  echo "Analyze recovery complete. You may need to re-run /milestone:analyze <milestone-number>."
fi

#### Implementation Phase Recovery

!if [ "$ARGUMENTS" = "implement" ]; then
  echo "=== IMPLEMENTATION PHASE RECOVERY ==="
  
  echo "1. Checking for syntax errors..."
  find easel/ -name "*.py" -exec python -m py_compile {} \; 2>&1 | head -10 || echo "Syntax check complete"
  
  echo "2. Checking import issues..."
  python -c "
import sys
sys.path.insert(0, 'easel')
try:
    import easel
    print('✅ Main imports working')
except Exception as e:
    print(f'❌ Import error: {e}')
  "
  
  echo "3. Checking test structure..."
  find tests/ -name "*.py" | head -5 || echo "No test files found"
  
  echo "4. Running basic validation..."
  poetry run pytest --collect-only -q | tail -5 || echo "Test collection issues detected"
  
  echo "5. Checking for incomplete implementations..."
  grep -r "TODO\|FIXME\|NotImplemented" easel/ | head -5 || echo "No obvious incomplete implementations"
  
  echo "Implementation recovery analysis complete."
  echo "Review errors above and fix issues before re-running /milestone:implement."
fi

#### Validation Phase Recovery

!if [ "$ARGUMENTS" = "validate" ]; then
  echo "=== VALIDATION PHASE RECOVERY ==="
  
  echo "1. Test Coverage Issues Recovery..."
  poetry run pytest --cov=easel --cov-report=term-missing | tail -10 || echo "Test execution failed"
  
  COVERAGE=$(poetry run coverage report | grep TOTAL | awk '{print $4}' 2>/dev/null || echo "0%")
  echo "Current coverage: $COVERAGE"
  
  if [[ $COVERAGE < "80%" ]]; then
    echo "❌ Coverage below 80% - need more tests"
    echo "Files with low coverage:"
    poetry run coverage report --show-missing | grep -E " [0-7][0-9]%" | head -5
  fi
  
  echo "2. Code Quality Issues Recovery..."
  echo "Black formatting issues:"
  poetry run black easel/ tests/ --check --diff | head -10 || echo "No formatting issues"
  
  echo "Flake8 linting issues:"
  poetry run flake8 easel/ tests/ | head -10 || echo "No linting issues"
  
  echo "MyPy type issues:"
  poetry run mypy easel/ | head -10 || echo "No type issues"
  
  echo "3. Acceptance Criteria Recovery..."
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ $CURRENT_BRANCH =~ milestone-([0-9]+) ]]; then
    MILESTONE_NUM=${BASH_REMATCH[1]}
    echo "Checking milestone $MILESTONE_NUM acceptance criteria:"
    grep -E "\[[ x]\]" specs/$MILESTONE_NUM-*.md | head -5 || echo "No acceptance criteria checklist found"
  fi
  
  echo "Validation recovery complete. Fix issues above before re-running /milestone:validate."
fi

#### Integration Phase Recovery

!if [ "$ARGUMENTS" = "integrate" ]; then
  echo "=== INTEGRATION PHASE RECOVERY ==="
  
  echo "1. Documentation Issues Recovery..."
  echo "Checking for missing docstrings..."
  grep -r "def " easel/ | grep -v "__" | head -5
  echo "Files that may need documentation updates:"
  git diff --name-only | head -5
  
  echo "2. CLI Integration Issues..."
  poetry run python -m easel --help || echo "❌ CLI not working"
  
  echo "3. Import Structure Issues..."
  python -c "
import sys
sys.path.insert(0, 'easel')
try:
    from easel.cli import main
    print('✅ CLI imports working')
except Exception as e:
    print(f'❌ CLI import error: {e}')
  "
  
  echo "4. Dependency Issues..."
  poetry check || echo "❌ Poetry configuration issues"
  poetry show --tree | head -10
  
  echo "Integration recovery complete. Fix issues above before re-running /milestone:integrate."
fi

#### Submission Phase Recovery

!if [ "$ARGUMENTS" = "submit" ]; then
  echo "=== SUBMISSION PHASE RECOVERY ==="
  
  echo "1. Git Issues Recovery..."
  git status --porcelain | wc -l | xargs echo "Uncommitted files:"
  
  echo "2. Branch Issues..."
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Current branch: $CURRENT_BRANCH"
  git branch -r | grep $CURRENT_BRANCH || echo "Branch not pushed to remote"
  
  echo "3. GitHub Issues..."
  gh auth status || echo "❌ GitHub authentication failed"
  
  if [[ $CURRENT_BRANCH =~ issue-([0-9]+) ]]; then
    ISSUE_NUM=${BASH_REMATCH[1]}
    echo "Checking issue #$ISSUE_NUM status:"
    gh issue view $ISSUE_NUM --json state,title | jq -r '"State: " + .state + ", Title: " + .title' 2>/dev/null || echo "Could not fetch issue"
  fi
  
  echo "4. PR Issues..."
  gh pr view 2>/dev/null && echo "PR exists" || echo "No PR found for this branch"
  
  echo "5. Quality Gate Recovery..."
  echo "Final test run:"
  poetry run pytest -q | tail -5 || echo "Tests failing"
  
  echo "Submission recovery complete. Review issues above."
  echo "You may need to:"
  echo "- Fix failing tests"
  echo "- Commit remaining changes"
  echo "- Re-run /milestone:submit"
fi

### General Recovery Actions

#### 2. Reset and Clean Recovery

!echo ""
!echo "=== GENERAL RECOVERY ACTIONS ==="

!echo "1. Clean temporary files..."
!find . -name "*.pyc" -delete
!find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
!find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

!echo "2. Poetry environment refresh..."
!poetry env info
!echo "Consider running: poetry install --with dev"

!echo "3. Pre-commit refresh..."
!poetry run pre-commit clean || echo "Pre-commit not available"
!echo "Consider running: poetry run pre-commit install"

#### 3. Emergency Reset Procedures

!echo ""
!echo "=== EMERGENCY RECOVERY OPTIONS ==="
!echo "If recovery fails, consider these options:"
!echo ""
!echo "🔄 Soft Reset (preserves work):"
!echo "   git stash"
!echo "   git clean -fd"
!echo "   poetry install --with dev"
!echo "   git stash pop"
!echo ""
!echo "⚠️  Hard Reset (loses uncommitted work):"
!echo "   git reset --hard HEAD"
!echo "   git clean -fd"
!echo "   poetry install --with dev"
!echo ""
!echo "🚨 Nuclear Reset (start milestone over):"
!echo "   git checkout main"
!echo "   git branch -D [feature-branch]"
!echo "   /milestone:analyze <milestone-number>"

### Escalation Protocol

#### 4. When to Escalate

!echo ""
!echo "=== ESCALATION PROTOCOL ==="
!echo "Escalate to human review if:"
!echo "- 3+ recovery attempts have failed"
!echo "- Security vulnerabilities detected"
!echo "- Architectural decisions needed"
!echo "- External dependencies broken"
!echo ""
!echo "To escalate:"
!echo "1. Document the specific failure in detail"
!echo "2. Create draft PR with current progress"
!echo "3. Add comment requesting human review"
!echo "4. Tag issue with 'needs-review' label"

### Recovery Success Validation

#### 5. Verify Recovery

!echo ""
!echo "=== RECOVERY VALIDATION ==="
!echo "After recovery, verify with:"
!echo "- /milestone:doctor (health check)"
!echo "- Re-run the failed phase command"
!echo "- Check all quality gates pass"

!echo ""
!echo "Recovery analysis complete for phase: $ARGUMENTS"
!echo "Review the guidance above and take appropriate action."