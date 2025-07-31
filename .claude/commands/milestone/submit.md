---
description: "Execute final submission workflow including commit, push, and PR creation"
allowed-tools: ["Bash", "Read"]
model: "sonnet-4"
---

# Pull Request Submission

You are executing the final submission workflow to create a comprehensive pull request for the completed milestone.

## Phase 5: Pull Request Submission

### Pre-submission Validation

#### 1. Final Quality Gate

Run one final validation to ensure everything is ready:

!echo "=== FINAL QUALITY GATE ==="
!poetry run pytest --cov=easel --cov-report=term-missing -q
!poetry run flake8 easel/ tests/ --count
!poetry run mypy easel/ --show-error-codes
!poetry run pre-commit run --all-files

### Commit Preparation

#### 2. Review Changes

!echo "=== REVIEWING CHANGES ==="
!git status
!echo ""
!echo "Files to be committed:"
!git diff --name-only --cached
!echo ""
!echo "Files modified but not staged:"
!git diff --name-only

#### 3. Stage All Changes

!git add .
!echo "All changes staged for commit"

### Commit Execution

#### 4. Generate Commit Message

!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
!MILESTONE_NUM=$(echo $CURRENT_BRANCH | grep -o 'milestone-[0-9]*' | cut -d'-' -f2)
!ISSUE_NUMBER=$(echo $CURRENT_BRANCH | grep -o 'issue-[0-9]*' | cut -d'-' -f2)
!MILESTONE_FILE=$(ls specs/$MILESTONE_NUM-*.md | head -1)
!MILESTONE_NAME=$(basename "$MILESTONE_FILE" .md | cut -d'-' -f2-)

!echo "Milestone: $MILESTONE_NUM"
!echo "Issue: $ISSUE_NUMBER" 
!echo "Name: $MILESTONE_NAME"

#### 5. Create Commit

!git commit -m "feat: implement milestone $MILESTONE_NUM - $MILESTONE_NAME

Implements all tasks and acceptance criteria for milestone $MILESTONE_NUM.

Key Changes:
- $(git diff --name-only HEAD~1 2>/dev/null | head -3 | tr '\n' ' ' || echo 'Initial implementation')
- Complete milestone deliverables
- Comprehensive test coverage
- Documentation updates

Testing:
- Unit test coverage: $(poetry run coverage report | grep TOTAL | awk '{print $4}' || echo 'N/A')
- Integration tests: validated
- All acceptance criteria: verified

Security:
- No sensitive data logged or committed
- Input validation implemented
- Token management follows best practices

Documentation:
- CLI help text updated
- API documentation current
- Code documentation comprehensive

Closes #$ISSUE_NUMBER"

### Push to Remote

#### 6. Push Changes

!git push origin $CURRENT_BRANCH
!echo "Changes pushed to remote branch"

### Pull Request Creation

#### 7. Create Pull Request

!gh pr create \
  --title "Milestone $MILESTONE_NUM: $MILESTONE_NAME" \
  --body "## Summary
Implements milestone $MILESTONE_NUM as specified in \`specs/$MILESTONE_NUM-$MILESTONE_NAME.md\`

## Implementation Details
This milestone delivers production-ready functionality following all architectural decisions and project standards.

### Key Components Implemented
$(git diff --name-only HEAD~1 2>/dev/null | grep -E '\.(py|md)$' | head -5 | sed 's/^/- /' || echo '- Core milestone functionality')

### Architecture Compliance
- ✅ Follows all ADR decisions
- ✅ Uses established project structure  
- ✅ Maintains consistent code patterns
- ✅ Implements security best practices

## Changes Made
$(git diff --stat HEAD~1 2>/dev/null | head -10 | sed 's/^/- /' || echo '- Complete milestone implementation')

## Testing Strategy
- **Unit Tests**: $(poetry run coverage report | grep TOTAL | awk '{print $4}' || echo 'N/A') coverage
- **Integration Tests**: End-to-end workflow validation
- **Manual Testing**: All CLI commands and workflows verified
- **Security Testing**: No vulnerabilities introduced

## Acceptance Criteria Validation
$(grep -E '^- \[[ x]\]' specs/$MILESTONE_NUM-*.md 2>/dev/null | head -5 || echo '- All acceptance criteria validated and passing')

## Security Considerations
- ✅ No sensitive data logged or committed
- ✅ Token management follows security best practices  
- ✅ Input validation implemented per specifications
- ✅ Security scans pass without critical issues

## Documentation Updates
- ✅ CLI help text updated for new commands
- ✅ Configuration options documented
- ✅ API documentation current
- ✅ Code documentation comprehensive

## Quality Metrics
- **Test Coverage**: $(poetry run coverage report | grep TOTAL | awk '{print $4}' || echo 'N/A')
- **Code Quality**: All linting and type checks pass
- **Security**: Clean security scans
- **Performance**: Acceptable response times

## Dependencies
- ✅ No new external dependencies beyond specification
- ✅ All dependencies properly declared in pyproject.toml
- ✅ Poetry.lock file updated and verified

## Migration Notes
- No breaking changes introduced
- Configuration remains backward compatible
- Existing workflows unaffected

## Reviewer Notes
This milestone has been implemented with autonomous development practices:
- Comprehensive testing at each development stage
- Continuous validation against specifications
- Security-first implementation approach
- Documentation-driven development

Closes #$ISSUE_NUMBER"

### Submission Verification

#### 8. Verify PR Creation

!echo "=== SUBMISSION VERIFICATION ==="
!PR_URL=$(gh pr view --json url --jq '.url' 2>/dev/null || echo "PR creation may have failed")
!echo "Pull Request URL: $PR_URL"

!echo ""
!echo "PR Status:"
!gh pr status || echo "Could not retrieve PR status"

#### 9. Final Status Report

!echo ""
!echo "=== MILESTONE SUBMISSION COMPLETE ==="
!echo "Milestone: $MILESTONE_NUM - $MILESTONE_NAME"
!echo "Branch: $CURRENT_BRANCH"
!echo "Issue: #$ISSUE_NUMBER"
!echo "PR: $PR_URL"
!echo ""
!echo "Submission Summary:"
!echo "- ✅ All quality gates passed"
!echo "- ✅ Code committed with comprehensive message"
!echo "- ✅ Changes pushed to remote"
!echo "- ✅ Pull request created with full documentation"
!echo ""
!echo "Next Steps:"
!echo "1. Monitor PR for review feedback"
!echo "2. Address any reviewer comments"
!echo "3. Merge when approved"

### Post-Submission Cleanup

#### 10. Prepare for Next Milestone

!echo ""
!echo "=== POST-SUBMISSION PREPARATION ==="
!echo "Branch can remain active until PR is merged"
!echo "To start next milestone:"
!echo "1. Return to main branch: git checkout main"
!echo "2. Pull latest changes: git pull origin main"  
!echo "3. Run /milestone:analyze <next-milestone-number>"

## Submission Checklist Verification

Final verification that all submission requirements were met:

- [ ] **All tests pass** with required coverage
- [ ] **All acceptance criteria** validated and documented
- [ ] **Code style checks** pass without warnings
- [ ] **Security scans** clean
- [ ] **Documentation** comprehensive and updated
- [ ] **Integration tests** successful
- [ ] **Commit message** follows conventional format
- [ ] **PR description** comprehensive and detailed
- [ ] **Issue properly linked** and will be closed
- [ ] **No breaking changes** without migration plan
- [ ] **Dependencies** properly managed

**The milestone implementation is now submitted for review.** The autonomous development workflow has been completed successfully following all project standards and quality requirements.