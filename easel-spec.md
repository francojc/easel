# Easel CLI Technical Specification

**Version:** 0.1  
**Status:** Draft  
**Author:** Jerid Francom 
**Date:** 2025-07-31 

## Overview

Easel is a Python-based CLI tool providing programmatic access to Canvas LMS via REST API. The tool prioritizes safety, extensibility, and automation workflows for educational institutions.

### Technical Requirements

- **Runtime:** Python 3.8+
- **Dependencies:** Click, httpx, rich, PyYAML
- **Distribution:** PyPI package with optional Docker container
- **Architecture:** Plugin-based modular design
- **API:** Canvas REST API v1

### Success Criteria

- Complete read-only Canvas API coverage
- Sub-second response for cached operations
- Simplified single-institution setup
- Shell integration (completion, exit codes, piping)

---

## Architecture

### Core Components

```
easel/
├── cli/                 # Click command definitions
├── api/                 # Canvas API client
├── config/              # Configuration management
├── formatters/          # Output formatting
├── plugins/             # Extensibility system
└── utils/               # Shared utilities
```

### Data Flow

```
CLI Input → Validation → API Client → Canvas API → Response Processing → Formatter → Output
```

### Authentication Flow

- Configuration storage (`~/.easel/config.yaml` or `~/.config/easel/config.yaml`)
- Token-based authentication with refresh capability
- OAuth2 support (future enhancement)

---

## Implementation Roadmap

### Phase 1: Core Infrastructure

**Deliverables:**

- [ ] Project scaffolding with Poetry
- [ ] Click-based command framework
- [ ] Configuration management system
- [ ] Canvas API client with rate limiting
- [ ] Basic authentication flow
- [ ] Configuration validation command (`easel doctor`)

**Acceptance Criteria:**

- `easel init` invokes an interactive configuration wizard to set up the institution
- API client handles rate limits and pagination
- Configuration stores credentials for a single institution

### Phase 2: Read-Only Commands

**Deliverables:**

- [ ] Course operations (`list`, `show`, `modules`)
- [ ] Assignment operations (`list`, `show`, `submissions`)
- [ ] User operations (`profile`, `courses`, `roster`)
- [ ] Output formatting (table, JSON, CSV, YAML)

**Acceptance Criteria:**

- All commands support `--format` flag
- Pagination handled transparently
- Error messages are actionable

### Phase 3: Data Export & Analytics

**Deliverables:**

- [ ] Grade export functionality
- [ ] Content listing and metadata
- [ ] Basic analytics commands
- [ ] Bulk download capabilities

**Acceptance Criteria:**

- CSV exports compatible with Excel
- Large datasets stream without memory issues
- Progress indicators for long operations

### Phase 4: Automation Features

**Deliverables:**

- [ ] Timestamp-based filtering (`--since`)
- [ ] Status-based filtering (`--active`, `--overdue`)
- [ ] Scripting-friendly exit codes
- [ ] JSON output optimization

**Acceptance Criteria:**

- Commands integrate cleanly with shell scripts
- JSON output pipes correctly to `jq`
- Exit codes follow UNIX conventions

### Phase 5: Production Readiness

**Deliverables:**

- [ ] Comprehensive error handling
- [ ] Caching layer with configurable TTL
- [ ] Request/response logging
- [ ] Performance optimization

**Acceptance Criteria:**

- 95% test coverage
- Sub-100ms response for cached data
- Graceful degradation on API failures

### Phase 6: Distribution

**Deliverables:**

- [ ] PyPI packaging
- [ ] Shell completion scripts
- [ ] Docker containerization
- [ ] Documentation and examples

**Acceptance Criteria:**

- One-command installation via pip
- Tab completion works in bash/zsh
- Docker image < 100MB

---

## API Design

### Command Structure

```bash
easel [global-options] <resource> <action> [resource-id] [action-options]
```

### Global Options

- `--config PATH`: Configuration file path
- `--format FORMAT`: Output format (table|json|csv|yaml)
- `--verbose`: Detailed logging
- `--dry-run`: Preview mode (future)

### Resource Commands

```bash
# Configuration
easel init                              # Setup wizard
easel config list                       # Show configuration
easel doctor                           # Validate setup

# Courses
easel course list [--active]           # List courses
easel course show <course-id>          # Course details
easel course modules <course-id>       # Module structure

# Assignments
easel assignment list <course-id>      # List assignments
easel assignment show <course-id> <assignment-id>
easel assignment submissions <course-id> <assignment-id> [--since DATE] [--download-all] [--output PATH]

# Grades
easel grade export <course-id> [--format csv]
easel grade analytics <course-id>

# Users
easel user profile                     # Current user
easel user roster <course-id>          # Course roster
```

### Scripting Examples

```bash
# Daily grade backup
easel grade export CS101 --format csv > "grades-$(date +%Y%m%d).csv"

# Bulk submission download
easel assignment submissions CS101 hw-final --download-all --output ./submissions/

# Integration pipeline
easel course list --format json | jq -r '.[].id' | \
    xargs -I {} easel grade analytics {} --format json > analytics.json
```

---

## Technical Decisions

### Libraries

- **Click**: Command framework (vs argparse - better UX)
- **httpx**: HTTP client (vs requests - async ready)
- **rich**: Terminal formatting (vs tabulate - better progress bars)
- **PyYAML**: Configuration (vs TOML - Canvas ecosystem standard)

### Design Patterns

- **Command Pattern**: Each CLI command as separate class
- **Factory Pattern**: Output formatters
- **Strategy Pattern**: Authentication methods
- **Plugin Architecture**: Extension points via entry_points

### Error Handling Strategy

1. Network errors → Retry with exponential backoff
2. API errors → Map to user-friendly messages
3. Input validation → Early failure with suggestions
4. Configuration errors → Interactive fixes when possible

---

## Security Considerations

### Token Management

- Tokens stored in `~/.easel/` or `~/.config/easel/` with 600 permissions
- Support for environment variable override
- Automatic token rotation (when Canvas supports it)

### Data Handling

- No sensitive data in logs by default
- Configurable log levels and redaction
- Memory-safe handling of large datasets

---

## Testing Strategy

### Unit Tests (pytest)

- API client mocking with respx library
- Command testing with Click's testing utilities
- Configuration management edge cases

### Integration Tests

- Mock Canvas API with realistic responses
- End-to-end command workflows
- Configuration management scenarios

### Performance Tests

- Large dataset handling (1000+ courses)
- Concurrent request behavior
- Memory usage profiling

---

## Deployment & Distribution

### PyPI Package

```bash
pip install easel-cli
easel init
```

### Docker Container

```bash
docker run -v ~/.easel:/root/.easel easel-cli course list
```

### Shell Integration

```bash
# bash/zsh completion
eval "$(easel --completion bash)"
```

---

## Future Enhancements (Post-MVP)

### Write Operations (Phase 7)

- Assignment CRUD operations
- Grade upload with validation
- Bulk enrollment management
- Content upload capabilities

### Advanced Features

- GraphQL support (when Canvas adds it)
- Real-time data sync via webhooks
- Advanced analytics and reporting
- Integration with external gradebooks

---

## Success Metrics

### Performance Targets

- Command execution: < 2s for uncached operations
- Memory usage: < 50MB for typical workflows
- Test coverage: > 95%

### User Experience Goals

- Simplified setup for single institution
- Self-documenting help system
- Consistent output formatting across commands
