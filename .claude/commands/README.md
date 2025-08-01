# Easel CLI Milestone Development Commands

This directory contains custom Claude Code slash commands for autonomous milestone development on the **Easel CLI** project. These commands implement the complete development workflow specified in `milestone-agent.md`.

## ⚡ IMPORTANT: Sub-Agent Migration

**Complex milestone commands have been converted to specialized sub-agents** for enhanced conversational capabilities and expert assistance. See [Sub-Agents Documentation](../subagents/README.md) for details.

**Converted to Sub-Agents:**
- `/milestone:doctor` → `@doctor` sub-agent
- `/milestone:implement` → `@implementation-specialist` sub-agent
- `/milestone:validate` → `@qa-specialist` sub-agent
- `/milestone:recover` → `@troubleshooting-specialist` sub-agent

**Remaining as Slash Commands:**
- `/milestone:setup`, `/milestone:analyze`, `/milestone:integrate`, `/milestone:submit`

## Command Overview

### Core Workflow Commands

| Command | Purpose | Phase | Dependencies |
|---------|---------|-------|--------------|
| `/milestone:setup` | Initialize development environment | Pre-development | None |
| `/milestone:analyze <N>` | Create issue and feature branch | Phase 1 | setup complete |
| `@implementation-specialist` | Execute implementation (sub-agent) | Phase 2 | analyze complete |
| `@qa-specialist` | Quality assurance validation (sub-agent) | Phase 3 | implement complete |
| `/milestone:integrate` | Integration testing & docs | Phase 4 | validate complete |
| `/milestone:submit` | Create pull request | Phase 5 | integrate complete |

### Supporting Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `@doctor` | Health check and diagnostics (sub-agent) | Any time, especially when troubleshooting |
| `@troubleshooting-specialist` | Error recovery procedures (sub-agent) | When a phase fails |

### Project Utility Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/easel:test` | Comprehensive test suite with coverage reporting | After code changes, before commits |
| `/easel:docs` | Documentation generation and validation | When updating documentation |
| `/easel:release` | Release preparation and artifact building | Before creating releases |

### Specialized Domain Sub-Agents

| Sub-Agent | Purpose | When to Use |
|-----------|---------|-------------|
| `@analytics-specialist` | Canvas data analysis and export optimization | Milestone 3, data export features |
| `@security-specialist` | Security analysis and educational compliance | Security reviews, compliance validation |

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

Execute the milestone implementation using the specialized sub-agent:

```bash
@implementation-specialist
```

This sub-agent provides conversational implementation guidance:
- Following architectural compliance requirements
- Implementing tasks in dependency order
- Writing tests alongside implementation
- Maintaining code quality standards
- Security best practices

### 4. Quality Validation

Run comprehensive quality assurance using the specialized sub-agent:

```bash
@qa-specialist
```

This sub-agent provides intelligent validation:
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

1. **Use the troubleshooting sub-agent**: `@troubleshooting-specialist`
2. **Provide the failed phase context** for targeted recovery guidance
3. **Follow the systematic recovery procedures**
4. **Re-run the failed phase** after issues are resolved
5. **Only proceed after successful completion**

### Health Monitoring

Use `@doctor` regularly to:
- Monitor environment health
- Identify potential issues early
- Validate configuration
- Check development context

### Development Utilities

**Testing and Quality Assurance:**
- Use `/easel:test` after making code changes to run comprehensive testing
- Run quality checks and coverage analysis before committing
- Validate security and code style standards

**Documentation Management:**
- Use `/easel:docs` when updating project documentation
- Generate API documentation and validate help text
- Check documentation links and accuracy

**Release Management:**
- Use `/easel:release` when preparing for version releases
- Build and validate distribution packages
- Run comprehensive pre-release quality gates

### Specialized Domain Support

**Canvas Data Analytics (Milestone 3):**
- Use `@analytics-specialist` for data export strategy design
- Get expert guidance on Canvas API optimization
- Implement educational analytics with performance considerations

**Security and Compliance:**
- Use `@security-specialist` for security reviews
- Validate FERPA and educational privacy compliance
- Get guidance on secure coding practices for educational data

## Command Arguments

### `/milestone:analyze <milestone-number>`
- **Required**: Milestone number (1-6 based on specs)
- **Example**: `/milestone:analyze 3`

### Sub-Agent Invocation
Sub-agents are invoked by name and provide conversational interfaces:

**Milestone Development:**
- **`@doctor`**: Environment health assessment
- **`@implementation-specialist`**: Implementation guidance and assistance
- **`@qa-specialist`**: Quality assurance and validation
- **`@troubleshooting-specialist`**: Error recovery and troubleshooting

**Specialized Domain Experts:**
- **`@analytics-specialist`**: Canvas data analysis and export optimization
- **`@security-specialist`**: Security analysis and educational compliance

### Project Utility Commands
Project-specific utility commands for common development tasks:
- **`/easel:test`**: Comprehensive testing with coverage reports and quality checks
- **`/easel:docs`**: Documentation generation, validation, and link checking
- **`/easel:release`**: Release preparation, artifact building, and distribution validation

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
