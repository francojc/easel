# Easel CLI Milestone Development Commands

This directory contains custom Claude Code slash commands for autonomous milestone development on the **Easel CLI** project. These commands implement the complete development workflow specified in `milestone-agent.md`.

## Command Overview

### Core Workflow Commands

| Command | Purpose | Phase | Dependencies |
|---------|---------|-------|--------------|
| `/milestone:setup` | Initialize development environment | Pre-development | None |
| `/milestone:analyze <N>` | Create issue and feature branch | Phase 1 | setup complete |
| `/milestone:implement` | Execute implementation | Phase 2 | analyze complete |
| `/milestone:validate` | Quality assurance validation | Phase 3 | implement complete |
| `/milestone:integrate` | Integration testing & docs | Phase 4 | validate complete |
| `/milestone:submit` | Create pull request | Phase 5 | integrate complete |

### Supporting Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/milestone:doctor` | Health check and diagnostics | Any time, especially when troubleshooting |
| `/milestone:recover <phase>` | Error recovery procedures | When a phase fails |

## Complete Workflow Guide

### 1. Initial Setup (One-time)

First, ensure your development environment is properly configured:

```bash
/milestone:setup
```

This command will:
- Verify all prerequisites (Python, Poetry, Git, GitHub CLI)
- Install dependencies
- Configure pre-commit hooks
- Validate environment readiness

### 2. Starting a New Milestone

To begin work on a specific milestone:

```bash
/milestone:analyze 1
```

Replace `1` with your target milestone number. This command will:
- Read the milestone specification from `specs/01-*.md`
- Review architectural decisions in `adr/`
- Create a GitHub issue
- Create and switch to a feature branch
- Set up the development context

### 3. Implementation

Execute the milestone implementation:

```bash
/milestone:implement
```

This command guides you through:
- Following architectural compliance requirements
- Implementing tasks in dependency order
- Writing tests alongside implementation
- Maintaining code quality standards
- Security best practices

### 4. Quality Validation

Run comprehensive quality assurance:

```bash
/milestone:validate
```

This validates:
- Test coverage (≥80% regular milestones, ≥95% production)
- Code quality (black, flake8, mypy)
- Security scans
- Acceptance criteria
- Performance benchmarks

### 5. Integration Preparation

Prepare for integration:

```bash
/milestone:integrate
```

This handles:
- Documentation updates
- CLI help text validation
- End-to-end workflow testing
- Cross-module integration checks
- Performance validation

### 6. Pull Request Submission

Submit the completed milestone:

```bash
/milestone:submit
```

This creates:
- Comprehensive commit message
- Detailed pull request
- Full documentation
- Links to related issues

## Workflow Best Practices

### Sequential Execution

**Always follow the phase sequence:**
1. setup → analyze → implement → validate → integrate → submit

**Never skip phases** - each builds on the previous one's validation.

### Quality Gates

Each phase has **mandatory quality gates** that must pass:

- **Setup**: All tools available and configured
- **Analyze**: Issue created, branch ready, specs understood  
- **Implement**: Code follows patterns, tests written, security validated
- **Validate**: Coverage targets met, all quality checks pass
- **Integrate**: Documentation current, integration tests pass
- **Submit**: PR created with comprehensive documentation

### Error Handling

When a phase fails:

1. **Use the recovery command**: `/milestone:recover <failed-phase>`
2. **Review the specific guidance** for that phase
3. **Fix the identified issues**
4. **Re-run the failed phase**
5. **Only proceed after successful completion**

### Health Monitoring

Use `/milestone:doctor` regularly to:
- Monitor environment health
- Identify potential issues early
- Validate configuration
- Check development context

## Command Arguments

### `/milestone:analyze <milestone-number>`
- **Required**: Milestone number (1-6 based on specs)
- **Example**: `/milestone:analyze 3`

### `/milestone:recover <phase>`
- **Required**: Phase name
- **Valid phases**: setup, analyze, implement, validate, integrate, submit
- **Example**: `/milestone:recover validate`

## Environment Requirements

### Prerequisites
- Python 3.8+
- Poetry
- Git
- GitHub CLI (`gh`)

### Project Structure
```
easel/
├── easel/           # Main package
├── tests/           # Test suite
├── specs/           # Milestone specifications
├── adr/             # Architectural decisions
├── pyproject.toml   # Dependencies
└── .claude/         # This commands directory
    └── commands/
        └── milestone/
```

### Quality Standards
- **Test Coverage**: ≥80% (≥95% for production milestones)
- **Code Quality**: All linting and type checks must pass
- **Security**: No vulnerabilities, no exposed secrets
- **Documentation**: Comprehensive docstrings and help text

## Troubleshooting

### Common Issues

#### Environment Problems
- **Solution**: Run `/milestone:doctor` to identify issues
- **Common fixes**: `poetry install --with dev`, `gh auth login`

#### Quality Gate Failures
- **Coverage too low**: Add more tests, focus on uncovered lines
- **Linting errors**: Run `poetry run black easel/ tests/`
- **Type errors**: Fix mypy issues before proceeding

#### Integration Failures
- **Import errors**: Check circular dependencies
- **CLI not working**: Verify entry points in pyproject.toml
- **Tests failing**: Run tests individually to isolate issues

#### GitHub Issues
- **Authentication**: `gh auth login`
- **Permissions**: Ensure write access to repository
- **Branch conflicts**: May need to rebase or merge main

### Recovery Strategies

1. **Incremental Recovery**: Fix one issue at a time
2. **Clean Environment**: Remove temporary files, reinstall deps
3. **Branch Reset**: Stash changes, clean working directory
4. **Nuclear Option**: Start milestone over from clean state

### Getting Help

If recovery attempts fail after 3 tries:
1. Document the specific failure
2. Create draft PR with current progress  
3. Add comment requesting human review
4. Tag issue with "needs-review" label

## Advanced Usage

### Customization

Commands can be customized by editing the `.md` files in `.claude/commands/milestone/`. Each command supports:
- Custom tool permissions via `allowed-tools`
- Model selection via `model`
- Argument hints via `argument-hint`

### Parallel Development

For working on multiple milestones:
1. Complete current milestone through submission
2. Return to main: `git checkout main`
3. Pull latest: `git pull origin main`
4. Start next: `/milestone:analyze <next-number>`

### Quality Optimization

For higher quality standards:
- Increase coverage targets in validation
- Add additional security scans
- Include performance benchmarking
- Extend integration test coverage

## Security Considerations

These commands follow strict security practices:
- **Never commit secrets or tokens**
- **Validate all user inputs**
- **Use secure token management**
- **Follow principle of least privilege**
- **Regular security scanning**

All commands are designed for **defensive security** only and will not assist with malicious activities.

---

**Remember**: These commands implement production-grade development workflows for educational institutions. Prioritize **correctness, security, and reliability** over speed. Every milestone delivery must meet the highest quality standards.