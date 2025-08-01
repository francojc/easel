---
description: "Execute milestone implementation following architectural compliance and code standards"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
---

# Milestone Implementation Strategy

You are implementing the current milestone following strict architectural compliance and established code patterns.

## Phase 2: Implementation Strategy

### Architectural Compliance Requirements

You **MUST** follow these requirements exactly:
- Follow all ADR decisions exactly
- Use established project structure (`easel/cli/`, `easel/api/`, `easel/config/`, etc.)
- Maintain consistent code style and patterns
- Implement security best practices (no secrets in logs/commits)

### Review Current Project Structure

First, understand the existing codebase structure:

!find easel/ -type f -name "*.py" | head -20
@easel/

### Code Implementation Standards

Follow the established patterns in the codebase. Here's the pattern you must follow:

```python
import click
from typing import Optional
from easel.api.client import CanvasClient
from easel.config import get_config

@click.command()
@click.option('--format', type=click.Choice(['json', 'table', 'csv']), default='table')
def command_example(format: str) -> None:
    """Example command following project patterns."""
    config = get_config()
    client = CanvasClient(config)
    # Implementation follows existing patterns...
```

### Task Execution Strategy

1. **Read all milestone tasks** from the current milestone specification
2. **Implement tasks in dependency order** (foundational first)
3. **Follow existing code patterns exactly**
4. **Write tests for each component as you build**
5. **Validate continuously** (don't accumulate technical debt)

### Implementation Process

#### Step 1: Review Milestone Tasks
Read the milestone specification to understand all deliverables:

!CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
!MILESTONE_NUM=$(echo $CURRENT_BRANCH | grep -o 'milestone-[0-9]*' | cut -d'-' -f2)
!ls specs/$MILESTONE_NUM-*.md
@specs/$MILESTONE_NUM-*.md

#### Step 2: Examine Existing Code Patterns
Study how similar functionality is implemented:

@easel/cli/
@easel/api/
@easel/config/

#### Step 3: Implement Core Components
Start with foundational components and work up to user-facing features:

1. **Data Models** (if needed)
2. **API Client Extensions** (if needed)
3. **CLI Commands**
4. **Configuration Options**
5. **Error Handling**

#### Step 4: Follow Test-Driven Development
For each component you implement:

1. **Write tests first** or alongside implementation
2. **Run tests frequently**: `!poetry run pytest -xvs`
3. **Maintain coverage**: Aim for >80% coverage

#### Step 5: Continuous Validation
After implementing each major component:

!poetry run pytest --cov=easel --cov-report=term-missing
!poetry run black easel/ tests/
!poetry run flake8 easel/ tests/
!poetry run mypy easel/

### Security Best Practices

- **Never log or commit secrets**
- **Validate all user inputs**
- **Use secure token management**  
- **Follow principle of least privilege**

### Error Handling Patterns

Follow the project's established error handling:

```python
try:
    # Canvas API operation
    result = client.get_courses()
except CanvasAPIError as e:
    click.echo(f"Error: {e}", err=True)
    return 1
except Exception as e:
    click.echo(f"Unexpected error: {e}", err=True)
    return 1
```

## Implementation Checklist

As you implement, ensure:

- [ ] All milestone deliverables are implemented
- [ ] Code follows existing patterns and conventions
- [ ] Tests are written for new functionality
- [ ] Error handling is comprehensive
- [ ] Security best practices are followed
- [ ] Documentation strings are complete
- [ ] Integration points work correctly

## Next Steps

After completing implementation:

1. Run comprehensive validation: `/milestone:validate`
2. Prepare integration and documentation: `/milestone:integrate`
3. Submit pull request: `/milestone:submit`

Remember: **Prioritize correctness, security, and reliability over speed.** Every line of code must meet production standards for educational institutions.