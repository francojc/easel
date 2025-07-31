---
description: "Comprehensive health check and diagnostic validation for milestone development environment"
allowed-tools: ["Bash", "Read", "Glob"]
model: "sonnet-4"
---

# Milestone Development Health Check

You are running comprehensive diagnostics to verify the health and readiness of the milestone development environment.

## System Health Diagnostics

### 1. Development Environment Status

!echo "=== DEVELOPMENT ENVIRONMENT HEALTH CHECK ==="

#### Prerequisites Check
!echo "1. Checking prerequisites..."
!python --version 2>/dev/null || echo "❌ Python not found"
!poetry --version 2>/dev/null || echo "❌ Poetry not found"  
!git --version 2>/dev/null || echo "❌ Git not found"
!gh --version 2>/dev/null || echo "❌ GitHub CLI not found"

#### Project Structure Validation
!echo ""
!echo "2. Validating project structure..."
!test -f "pyproject.toml" && echo "✅ pyproject.toml found" || echo "❌ pyproject.toml missing"
!test -d "easel" && echo "✅ easel/ directory found" || echo "❌ easel/ directory missing"
!test -d "tests" && echo "✅ tests/ directory found" || echo "❌ tests/ directory missing"
!test -d "specs" && echo "✅ specs/ directory found" || echo "❌ specs/ directory missing"
!test -d "adr" && echo "✅ adr/ directory found" || echo "❌ adr/ directory missing"

### 2. Git Repository Status

!echo ""
!echo "3. Git repository status..."
!git status --porcelain | wc -l | xargs echo "Modified files:"
!git branch --show-current | xargs echo "Current branch:"
!git remote -v | head -1 | xargs echo "Remote repository:"
!git log --oneline -3 | head -3

### 3. Poetry Environment Status

!echo ""
!echo "4. Poetry environment status..."
!poetry env info 2>/dev/null || echo "Poetry environment not initialized"
!poetry show --tree | head -10 2>/dev/null || echo "Dependencies not installed"

### 4. Testing Framework Status

!echo ""
!echo "5. Testing framework validation..."
!poetry run pytest --version 2>/dev/null || echo "❌ pytest not available"
!poetry run coverage --version 2>/dev/null || echo "❌ coverage not available"

!echo "Running quick test validation..."
!poetry run pytest --collect-only -q 2>/dev/null | tail -1 || echo "No tests found or pytest not working"

### 5. Code Quality Tools Status

!echo ""
!echo "6. Code quality tools validation..."
!poetry run black --version 2>/dev/null || echo "❌ black not available"
!poetry run flake8 --version 2>/dev/null || echo "❌ flake8 not available"  
!poetry run mypy --version 2>/dev/null || echo "❌ mypy not available"
!poetry run pre-commit --version 2>/dev/null || echo "❌ pre-commit not available"

### 6. Milestone Specifications Status

!echo ""
!echo "7. Milestone specifications status..."
!ls specs/ | wc -l | xargs echo "Available milestone specs:"
!ls specs/*.md 2>/dev/null | head -5 || echo "No milestone specs found"

### 7. Current Milestone Context

!echo ""
!echo "8. Current milestone context..."
!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
!echo "Current branch: $CURRENT_BRANCH"

!if [[ $CURRENT_BRANCH =~ milestone-([0-9]+) ]]; then
  MILESTONE_NUM=${BASH_REMATCH[1]}
  echo "Current milestone: $MILESTONE_NUM"
  test -f "specs/$MILESTONE_NUM-*.md" && echo "✅ Milestone spec found" || echo "❌ Milestone spec not found"
else
  echo "Not on a milestone branch"
fi

## Performance Diagnostics

### 8. System Performance Check

!echo ""
!echo "9. Performance diagnostics..."
!time poetry run python -c "import easel; print('✅ easel package imports successfully')" 2>/dev/null || echo "❌ easel package import failed"

## Security Diagnostics

### 9. Security Status Check

!echo ""
!echo "10. Security diagnostics..."
!echo "Checking for exposed credentials..."
!grep -r "password\|token\|secret\|key" easel/ --include="*.py" | grep -v "# " | wc -l | xargs echo "Potential credential exposures:"

!echo "Checking .gitignore coverage..."
!test -f ".gitignore" && echo "✅ .gitignore present" || echo "❌ .gitignore missing"

## Development Workflow Status

### 10. Workflow Status Check

!echo ""
!echo "11. Development workflow status..."

#### Check for active milestone work
!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
!if [[ $CURRENT_BRANCH =~ feature/issue-([0-9]+)-milestone-([0-9]+) ]]; then
  ISSUE_NUM=${BASH_REMATCH[1]}
  MILESTONE_NUM=${BASH_REMATCH[2]}
  echo "✅ Active milestone development detected"
  echo "   Issue: #$ISSUE_NUM"
  echo "   Milestone: $MILESTONE_NUM"
  
  echo "GitHub issue status:"
  gh issue view $ISSUE_NUM --json state,title | jq -r '"State: " + .state + ", Title: " + .title' 2>/dev/null || echo "Could not fetch issue status"
else
  echo "No active milestone development detected"
fi

#### Check for uncommitted work
!UNCOMMITTED=$(git status --porcelain | wc -l)
!if [ $UNCOMMITTED -gt 0 ]; then
  echo "⚠️  Uncommitted changes detected ($UNCOMMITTED files)"
  git status --porcelain | head -5
else
  echo "✅ Working directory clean"
fi

## Health Score Calculation

### 11. Overall Health Assessment

!echo ""
!echo "=== HEALTH SCORE ASSESSMENT ==="

!HEALTH_SCORE=0

# Prerequisites (20 points)
!command -v python >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!command -v poetry >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!command -v git >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!command -v gh >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))

# Project structure (20 points)
!test -f "pyproject.toml" && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!test -d "easel" && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!test -d "tests" && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!test -d "specs" && HEALTH_SCORE=$((HEALTH_SCORE + 5))

# Development tools (30 points)
!poetry run pytest --version >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 10))
!poetry run black --version >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!poetry run flake8 --version >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!poetry run mypy --version >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))
!poetry run pre-commit --version >/dev/null 2>&1 && HEALTH_SCORE=$((HEALTH_SCORE + 5))

# Working state (30 points)
!test $(git status --porcelain | wc -l) -eq 0 && HEALTH_SCORE=$((HEALTH_SCORE + 10))
!python -c "import easel" 2>/dev/null && HEALTH_SCORE=$((HEALTH_SCORE + 10))
!test -f ".gitignore" && HEALTH_SCORE=$((HEALTH_SCORE + 10))

!echo "Overall Health Score: $HEALTH_SCORE/100"

!if [ $HEALTH_SCORE -ge 90 ]; then
  echo "🟢 EXCELLENT - Environment is fully ready for milestone development"
elif [ $HEALTH_SCORE -ge 70 ]; then
  echo "🟡 GOOD - Environment is mostly ready, minor issues to address"
elif [ $HEALTH_SCORE -ge 50 ]; then
  echo "🟠 FAIR - Environment needs attention before milestone development"
else
  echo "🔴 POOR - Environment requires significant setup before proceeding"
fi

## Recommended Actions

### 12. Action Items

!echo ""
!echo "=== RECOMMENDED ACTIONS ==="

!if [ $HEALTH_SCORE -lt 100 ]; then
  echo "To improve environment health:"
  
  !command -v python >/dev/null 2>&1 || echo "- Install Python 3.8+"
  !command -v poetry >/dev/null 2>&1 || echo "- Install Poetry"
  !command -v git >/dev/null 2>&1 || echo "- Install Git"
  !command -v gh >/dev/null 2>&1 || echo "- Install GitHub CLI"
  
  !test -f "pyproject.toml" || echo "- Initialize Poetry project: poetry init"
  !test -d "easel" || echo "- Create easel/ package directory"
  !test -d "tests" || echo "- Create tests/ directory"
  
  !poetry run pytest --version >/dev/null 2>&1 || echo "- Install dev dependencies: poetry install --with dev"
  !test -f ".gitignore" || echo "- Create .gitignore file"
  
  !test $(git status --porcelain | wc -l) -eq 0 || echo "- Commit or stash uncommitted changes"
  
  echo ""
  echo "After addressing issues, re-run /milestone:doctor to verify improvements"
else
  echo "🎉 Environment is fully optimized for milestone development!"
  echo ""
  echo "Ready to proceed with:"
  echo "- /milestone:setup (if not already done)"
  echo "- /milestone:analyze <milestone-number> (to start new milestone)"
fi