# Development Implementation Details

**Project:** easel
**Status:** Phase 0 - Scaffolding
**Last Updated:** 2026-02-22

## Architecture

### System Design

- **Architecture Pattern:** CLI pipeline
- **Primary Language:** Python 3.11+
- **Framework:** Typer (CLI), httpx (HTTP), pydantic (validation)
- **Build System:** hatchling via pyproject.toml

### Component Overview

```
easel/
├── src/easel/            # Application source
│   ├── __init__.py       # __version__
│   ├── core/             # HTTP client, config, caching
│   │   ├── client.py     # CanvasClient (httpx async)
│   │   ├── config.py     # Config (pydantic-settings)
│   │   ├── cache.py      # CourseCache (code/ID mapping)
│   │   └── dates.py      # Date formatting utilities
│   ├── services/         # Async business logic per entity
│   │   ├── __init__.py   # CanvasError exception
│   │   ├── courses.py    # list, details, enrollments
│   │   ├── assignments.py
│   │   ├── rubrics.py
│   │   ├── grading.py
│   │   └── assessments.py
│   └── cli/              # Typer commands and helpers
│       ├── __init__.py
│       ├── app.py        # Main Typer app, global options
│       ├── _async.py     # asyncio.run() bridge decorator
│       ├── _output.py    # OutputFormat enum, format_output()
│       ├── _context.py   # Lazy init of client, cache, config
│       ├── courses.py    # Courses sub-app
│       ├── assignments.py
│       └── grading.py
├── tests/
│   ├── conftest.py       # Shared fixtures
│   ├── services/         # Service tests (mock CanvasClient)
│   └── cli/              # CLI tests (mock services, CliRunner)
├── specs/                # Planning and tracking
├── logs/                 # Session and weekly logs
├── pyproject.toml        # Build config and dependencies
├── flake.nix             # Nix development environment
└── CLAUDE.md             # Claude Code project instructions
```

### Key Modules

1. **core/client.py (CanvasClient)**
   - **Purpose:** Async HTTP client wrapping httpx for Canvas API
   - **Public Interface:** `request()`, `get_paginated()`,
     `test_connection()`, `close()`
   - **Dependencies:** httpx, core/config.py

2. **core/config.py (Config)**
   - **Purpose:** Load and validate Canvas API configuration
   - **Public Interface:** `Config` (pydantic BaseSettings),
     `validate()` method
   - **Dependencies:** pydantic-settings, python-dotenv

3. **core/cache.py (CourseCache)**
   - **Purpose:** Bidirectional mapping between course codes and IDs
   - **Public Interface:** `resolve()`, `refresh()`, `get_code()`,
     `get_id()`
   - **Dependencies:** core/client.py

4. **services/ (per-entity modules)**
   - **Purpose:** Async functions that call Canvas API, return
     structured data
   - **Public Interface:** Pure functions accepting CanvasClient,
     returning dicts/lists
   - **Dependencies:** core/client.py, raise CanvasError on failure

5. **cli/app.py (main app)**
   - **Purpose:** Typer app entry point, global options, sub-app
     registration
   - **Public Interface:** `app` (Typer instance), `--version`,
     `--test`, `--config`, `--format`
   - **Dependencies:** All cli/ sub-apps, cli/_context.py

### Data Model

- **Primary Data Structures:** Dicts and lists from Canvas API
  responses (no ORM)
- **Persistence Layer:** In-memory CourseCache, no local database
- **Serialization Format:** JSON for API communication and --format json
  output
- **Migration Strategy:** n/a (no local schema)

## Development Environment

### Setup

- **Language Runtime:** Python 3.11 via nix flake
- **Package Manager:** uv with pyproject.toml
- **Environment Management:** nix flake + direnv (`use flake`)
- **Local Services:** None (Canvas API is external)

### Build and Run

```bash
# Install dependencies
uv sync

# Run CLI
uv run easel --help
uv run easel courses list

# Run with specific format
uv run easel courses list --format json
```

### Code Standards

- **Formatting:** ruff format (`uv run ruff format src/ tests/`)
- **Linting:** ruff check (`uv run ruff check src/ tests/`)
- **Type Checking:** None initially (pydantic handles runtime validation)
- **Naming Conventions:** snake_case for functions/variables,
  PascalCase for classes

## Testing Strategy

### Test Levels

- **Service Tests:** pytest + pytest-asyncio, mock at CanvasClient
  level. Location: `tests/services/test_<entity>.py`
- **CLI Tests:** pytest + typer.testing.CliRunner, mock at service
  level. Location: `tests/cli/test_<entity>.py`

### Running Tests

```bash
# All tests
uv run pytest tests/

# Service tests only
uv run pytest tests/services/

# CLI tests only
uv run pytest tests/cli/

# With coverage
uv run pytest tests/ --cov=src/easel
```

### Coverage Targets

- **Overall:** 80%+
- **Critical Paths:** 90%+ for core/ (client, config, cache)
- **Exclusions:** CLI output formatting (visual, hard to assert)

### Test Data

- **Fixtures:** `tests/conftest.py` for shared fixtures
- **Mocks/Stubs:** unittest.mock for CanvasClient in service tests,
  service functions in CLI tests
- **Test Databases:** None (all external calls mocked)

## Deployment

### Target Environment

- **Platform:** Local CLI tool (pip/uv installable)
- **Runtime:** Python interpreter
- **Configuration:** `CANVAS_API_TOKEN` and `CANVAS_API_URL` env vars

### CI/CD Pipeline

- Not yet configured (single developer, local testing)

### Release Process

- **Versioning:** SemVer (0.x.y during initial development)
- **Changelog:** Maintained manually
- **Release Steps:** Tag, build with hatchling, install via uv/pip
- **Rollback Procedure:** `uv pip install` previous version

## Error Handling

- **Error Types:** `CanvasError` (base), HTTP errors from httpx
- **User-Facing Errors:** Formatted to stderr with non-zero exit codes
- **Error Reporting:** stderr output, no external reporting

## Security Considerations

### Authentication and Authorization

- **Auth Method:** Canvas API token via `CANVAS_API_TOKEN` env var
- **Permission Model:** Inherits Canvas user permissions
- **Secret Management:** Environment variable only, never read .env
  files programmatically in production, pydantic-settings handles
  loading

### Input Validation

- **User Input:** Typer handles CLI argument parsing and type coercion
- **API Boundaries:** pydantic validates config, CanvasClient validates
  HTTP responses

## Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-02-22 | Extract from canvas-mcp as reference only | Keeps easel independent, avoids coupling to MCP framework | Import canvas-mcp as library (rejected: too much MCP baggage) |
| 2026-02-22 | Use hatchling build backend | Lightweight, supports src layout natively | setuptools (heavier), flit (less flexible) |
| 2026-02-22 | Two test layers (services + CLI) | Clean separation, services test logic, CLI tests integration | Single test layer (insufficient coverage), three layers with tools/ (no MCP tools in easel) |
