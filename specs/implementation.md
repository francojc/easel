# Development Implementation Details

**Project:** easel
**Status:** Phase 5 - Modules, Pages, Discussions (COMPLETE)
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
│   │   ├── assessments.py
│   │   ├── modules.py
│   │   ├── pages.py
│   │   └── discussions.py
│   └── cli/              # Typer commands and helpers
│       ├── __init__.py
│       ├── app.py        # Main Typer app, global options
│       ├── _async.py     # asyncio.run() bridge decorator
│       ├── _output.py    # OutputFormat enum, format_output()
│       ├── _context.py   # Lazy init of client, cache, config
│       ├── courses.py    # Courses sub-app
│       ├── assignments.py
│       ├── grading.py
│       ├── assessments.py
│       ├── modules.py
│       ├── pages.py
│       └── discussions.py
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
     `validate_config()` method
   - **Dependencies:** pydantic-settings

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

6. **services/courses.py**
   - **Purpose:** Courses business logic (list, details, enrollments)
   - **Public Interface:** `list_courses()`, `get_course()`,
     `get_enrollments()` -- all async, accept CanvasClient
   - **Dependencies:** core/client.py, CanvasError

7. **cli/courses.py**
   - **Purpose:** Typer sub-app for course commands
   - **Public Interface:** `courses_app` with `list`, `show`,
     `enrollments` commands
   - **Dependencies:** services/courses.py, cli/_context.py,
     cli/_async.py, cli/_output.py

8. **services/assignments.py**
   - **Purpose:** Assignments business logic (list, get, create, update)
   - **Public Interface:** `list_assignments()`, `get_assignment()`,
     `create_assignment()`, `update_assignment()` -- all async
   - **Dependencies:** core/client.py, CanvasError
   - **Notes:** Includes `_strip_html()` helper for description cleanup

9. **services/rubrics.py**
   - **Purpose:** Rubrics business logic and form data encoding
   - **Public Interface:** `list_rubrics()`, `get_rubric()`,
     `build_rubric_assessment_form_data()` (sync helper)
   - **Dependencies:** core/client.py, CanvasError
   - **Notes:** `build_rubric_assessment_form_data()` handles Canvas
     bracket-notation encoding for rubric assessments

10. **services/grading.py**
    - **Purpose:** Submissions and grade posting
    - **Public Interface:** `list_submissions()`, `get_submission()`,
      `submit_grade()`, `submit_rubric_grade()` -- all async
    - **Dependencies:** core/client.py, services/rubrics.py, CanvasError

11. **cli/assignments.py**
    - **Purpose:** Typer sub-app for assignment and rubric commands
    - **Public Interface:** `assignments_app` with `list`, `show`,
      `create`, `update`, `rubrics`, `rubric` commands
    - **Dependencies:** services/assignments.py, services/rubrics.py

12. **cli/grading.py**
    - **Purpose:** Typer sub-app for grading commands
    - **Public Interface:** `grading_app` with `submissions`, `show`,
      `submit`, `submit-rubric` commands
    - **Dependencies:** services/grading.py

13. **services/assessments.py**
    - **Purpose:** Assessment workflow — build, load, save, update,
      submit assessment JSON files
    - **Public Interface:** `fetch_assignment_with_rubric()`,
      `fetch_submissions_with_content()`,
      `build_assessment_structure()`, `load_assessment()`,
      `save_assessment()`, `update_assessment_record()`,
      `get_assessment_stats()`, `submit_assessments()`
    - **Dependencies:** core/client.py, services/assignments.py
      (_strip_html), services/grading.py (submit_rubric_grade)

14. **cli/assessments.py**
    - **Purpose:** Typer sub-app for assessment workflow commands
    - **Public Interface:** `assess_app` with `setup`, `load`,
      `update`, `submit` commands
    - **Dependencies:** services/assessments.py

15. **services/modules.py**
    - **Purpose:** Modules business logic (list, get, create, update, delete)
    - **Public Interface:** `list_modules()`, `get_module()`,
      `create_module()`, `update_module()`, `delete_module()`
    - **Dependencies:** core/client.py, CanvasError
    - **Notes:** `get_module()` fetches items via separate paginated
      endpoint. Payload wrapped as `{"module": {...}}`

16. **cli/modules.py**
    - **Purpose:** Typer sub-app for module commands
    - **Public Interface:** `modules_app` with `list`, `show`,
      `create`, `update`, `delete` commands
    - **Dependencies:** services/modules.py

17. **services/pages.py**
    - **Purpose:** Pages business logic (list, get, create, update, delete)
    - **Public Interface:** `list_pages()`, `get_page()`,
      `create_page()`, `update_page()`, `delete_page()`
    - **Dependencies:** core/client.py, CanvasError
    - **Notes:** Pages identified by URL slug, not numeric ID.
      Includes `_strip_html()` for body cleanup. Payload wrapped
      as `{"wiki_page": {...}}`

18. **cli/pages.py**
    - **Purpose:** Typer sub-app for page commands
    - **Public Interface:** `pages_app` with `list`, `show`,
      `create`, `update`, `delete` commands
    - **Dependencies:** services/pages.py

19. **services/discussions.py**
    - **Purpose:** Discussions business logic (list, get, create, update)
    - **Public Interface:** `list_discussions()`, `get_discussion()`,
      `create_discussion()`, `update_discussion()`
    - **Dependencies:** core/client.py, CanvasError
    - **Notes:** Includes `_strip_html()` for message cleanup.
      Supports `only_announcements` filter. Flat JSON payload
      (no wrapper key)

20. **cli/discussions.py**
    - **Purpose:** Typer sub-app for discussion commands
    - **Public Interface:** `discussions_app` with `list`, `show`,
      `create`, `update` commands
    - **Dependencies:** services/discussions.py

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
- **Configuration:** `CANVAS_API_KEY` and `CANVAS_BASE_URL` env vars

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

- **Auth Method:** Canvas API token via `CANVAS_API_KEY` env var
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
| 2026-02-22 | Mock httpx at transport level | Tests actual request construction, cleaner than monkeypatching | respx library (extra dep), monkeypatch (fragile) |
| 2026-02-22 | CanvasClient class (not module functions) | Testable via DI, supports multiple configs, clean async lifecycle | Module-level functions like canvas-mcp (harder to test, global state) |
| 2026-02-22 | AsyncMock for service tests, patch get_context for CLI tests | Clean separation: service tests mock client, CLI tests mock services. No real config needed. | Transport-level mocks for CLI tests (too deep, couples layers) |
| 2026-02-22 | Rubric bracket-notation as a sync helper function | Reusable by grading service and future assessment workflow. Isolates Canvas encoding quirk. | Inline in grading service (harder to test), pydantic model (overkill) |
| 2026-02-22 | HTML stripping in assignments service | Canvas returns HTML descriptions; stripping at service level keeps CLI clean | Strip in CLI layer (duplicates logic), use a library like beautifulsoup (heavy dep for simple case) |
| 2026-02-22 | Assessment JSON as file-based interchange | Skills (assess:ai-pass, assess:refine) read/write JSON files; easel handles Canvas I/O, skills handle AI evaluation | Database (overkill), MCP tools (coupling), in-memory only (no persistence between skill invocations) |
| 2026-02-22 | Dry-run by default for assess submit | Prevents accidental grade submission; --confirm required for actual Canvas write | Auto-submit (dangerous), interactive prompt (harder to script) |
| 2026-02-22 | Copy _strip_html into each service that needs it | Keeps services self-contained, no cross-service imports for a trivial helper | Shared utility module (premature abstraction for 3-line function) |
| 2026-02-22 | Pages identified by URL slug, not numeric ID | Canvas API uses slugs for page endpoints; matches API semantics | Numeric IDs (not how Canvas pages work) |
| 2026-02-22 | Defer student commands | Instructor workflows don't need student-facing endpoints; keeps scope focused for 0.1.0 | Include student commands (scope creep, low priority) |
