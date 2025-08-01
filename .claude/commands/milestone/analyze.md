---
description: "Analyze milestone requirements and create GitHub issue with feature branch"
argument-hint: "<milestone-number>"
allowed-tools: ["Bash", "Read", "Glob"]
---

# Milestone Analysis & Issue Creation

You are analyzing and setting up development for milestone **$ARGUMENTS** of the Easel CLI project.

## Phase 1: Mission Analysis & Issue Creation

### 1. Read Target Milestone Specification

First, identify and read the milestone specification:

@specs/$ARGUMENTS-*.md

### 2. Architectural Review

Review all architectural decisions that will guide implementation:

@adr/

### 3. Project Context Review

Review the main project specification for context:

@easel-spec.md

## Create Development Infrastructure

### 4. Create GitHub Issue

Create a GitHub issue for this milestone:

!MILESTONE_FILE=$(ls specs/$ARGUMENTS-*.md | head -1)
!MILESTONE_NAME=$(basename "$MILESTONE_FILE" .md | cut -d'-' -f2-)
!gh issue create \
  --title "Milestone $ARGUMENTS: $MILESTONE_NAME" \
  --body-file "$MILESTONE_FILE" \
  --label "milestone,enhancement,agent-generated"

### 5. Capture Issue Number and Create Feature Branch

!ISSUE_NUMBER=$(gh issue list --limit 1 --json number --jq '.[0].number')
!echo "Created issue #$ISSUE_NUMBER"
!git checkout -b "feature/issue-$ISSUE_NUMBER-milestone-$ARGUMENTS-$(echo $MILESTONE_NAME | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')"
!git push -u origin "feature/issue-$ISSUE_NUMBER-milestone-$ARGUMENTS-$(echo $MILESTONE_NAME | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')"

### 6. Verify Setup

!git status
!echo "Analysis complete. Issue #$ISSUE_NUMBER created and feature branch ready."
!echo "Next step: Run /milestone:implement to begin implementation"

## Implementation Planning

Based on the milestone specification you just reviewed:

1. **Identify all deliverables** and acceptance criteria
2. **Map dependencies** between tasks
3. **Plan implementation order** (foundational components first)
4. **Identify testing requirements** and coverage targets
5. **Note any architectural decisions** that need to be followed

You are now ready to proceed with implementation. The GitHub issue and feature branch have been created following the project's conventions.
