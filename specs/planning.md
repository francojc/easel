# Development Project Planning

**Project:** easel
**Status:** In Progress
**Last Updated:** 2026-02-22

## Project Overview

### Software Description

- **Application Type:** CLI tool
- **Target Platform:** macOS / Linux (cross-platform Python)
- **Primary Language:** Python 3.11+
- **Key Libraries/Frameworks:** Typer, httpx, pydantic, pydantic-settings,
  rich, python-dateutil

### Problem Statement

- Canvas LMS operations (grading, course management, assignments) lack
  a terminal-native interface for scripting and automation.
- The canvas-mcp project proves the business logic works but couples it
  to FastMCP, limiting use outside MCP-aware clients.
- Instructors and Claude Code skills need a composable CLI that pipes
  JSON, runs in scripts, and works from any terminal.

### Goals and Non-Goals

#### Goals

- [ ] Full Canvas API coverage for common instructor workflows
      (courses, assignments, rubrics, grading, modules, discussions)
- [ ] Three output formats: table (human), JSON (machine), plain (simple)
- [ ] Scriptable and composable -- exit codes, stderr for errors,
      stdout for data
- [ ] Usable as a backend for Claude Code assess/* skills via
      `easel <cmd> --format json`

#### Non-Goals

- No GUI or TUI beyond formatted terminal output
- No MCP integration -- easel is a standalone CLI
- No anonymization, audit logging, or sandbox config (canvas-mcp concerns)
- No runtime dependency on canvas-mcp (reference only)

## Architecture and Design

### High-Level Architecture

- **Pattern:** CLI pipeline
- **Data Flow:** `Typer CLI -> services (async) -> core (HTTP, config, cache)`
- **Key Components:**
  - Core: `CanvasClient` (httpx), `Config` (pydantic-settings),
    `CourseCache` (code/ID mapping)
  - Services: async functions per Canvas entity, raise `CanvasError`
  - CLI: Typer commands that bridge async, format output, handle errors

### External Dependencies

- **APIs and Services:** Canvas LMS REST API
- **Data Sources:** Canvas API via httpx, local course cache
- **Build Tools:** uv (package manager), hatchling (build backend),
  ruff (linting/formatting)

### Technical Constraints

- Python 3.11+ required (asyncio improvements, ExceptionGroup)
- Canvas API rate limits: retry with backoff on HTTP 429
- Canvas API token required via environment variable
- Canvas rubric grading uses bracket-notation form data encoding

## Timeline and Milestones

### Phase 0: Scaffolding (COMPLETE)

- [x] Create pyproject.toml with hatchling build and entry point
- [x] Set up src/easel/ directory structure (core, services, cli)
- [x] Create Typer app skeleton with --version, --test, --config
- [x] Implement async bridging and output formatting
- [x] Verify `uv sync && uv run easel --help`

### Phase 1: Core Layer (COMPLETE)

- [x] Implement Config (pydantic-settings, env var loading)
- [x] Implement CanvasClient (httpx, pagination, retry on 429)
- [x] Implement CourseCache (bidirectional code/ID mapping)
- [x] Create CLI context (lazy init of client, cache, config)
- [x] Unit tests for core modules (24 tests)

### Phase 2: Courses (Proving Ground) (COMPLETE)

- [x] Implement courses service (list, details, enrollments)
- [x] Implement courses CLI commands
- [x] Service tests with mocked client
- [x] CLI tests with mocked services

### Phase 3: Assignments + Rubrics + Grading (COMPLETE)

- [x] Assignments service (list, get, create, update) with HTML stripping
- [x] Assignments CLI (list, show, create, update, rubrics, rubric)
- [x] Rubrics service (list, get, bracket-notation form data builder)
- [x] Grading service (submissions, get, submit grade, submit rubric grade)
- [x] Grading CLI (submissions, show, submit, submit-rubric)
- [x] Tests: 14 assignments svc, 8 rubrics svc, 10 grading svc,
  13 assignments CLI, 10 grading CLI (99 total)

### Phase 4: Assessment Workflow (COMPLETE)

- [x] Assessment service: fetch_assignment_with_rubric,
  fetch_submissions_with_content, build_assessment_structure,
  load/save/update_assessment, get_assessment_stats,
  submit_assessments
- [x] Assessment CLI: `easel assess setup|load|update|submit`
- [x] Setup builds full assessment JSON (metadata + rubric + submissions)
- [x] Submit uses dry-run by default, requires --confirm
- [x] Tests: 22 service, 12 CLI (133 total)

### Phase 5: Remaining Entity Groups

- [ ] Student commands (upcoming, grades, todo)
- [ ] Modules, discussions, pages, messaging, files
- [ ] Tests for each category

### Phase 6: Polish

- [x] Wire --test and --config callbacks (done in Phase 1)
- [ ] Shell completion support
- [ ] Final documentation pass

## Resources and Requirements

### Development Environment

- Python 3.11 via nix flake
- uv for package management and virtual environment
- ruff for linting and formatting
- direnv for automatic environment activation

### Infrastructure

- Local CLI tool -- no hosting required
- No CI/CD initially (single developer)
- Distribution via `uv pip install -e .`

### Collaboration

- Solo development with Claude Code assistance
- Feature branches, rebase workflow, squash merges

## Risk Assessment

### Technical Risks

- Canvas API changes could break assumptions copied from canvas-mcp.
  Mitigation: test against live API early (Phase 2).
- Async bridging in Typer can be tricky. Mitigation: isolate in
  `_async.py` decorator, test thoroughly.
- Rate limiting during batch grading. Mitigation: backoff in
  CanvasClient, respect 429 headers.

### Scope Risks

- Feature creep from canvas-mcp's full feature set. Guardrail:
  one-category-per-PR approach, defer non-essential entities.
- Assessment workflow complexity. Mitigation: Phase 4 is self-contained,
  can ship without it.

## Success Metrics

### Functional Criteria

- [ ] `easel courses list` returns live data in all three formats
- [ ] `easel assignments list <course> --format json` works for skills
- [ ] All implemented commands have service + CLI tests passing

### Quality Criteria

- [ ] ruff check and ruff format pass with no warnings
- [ ] Test coverage for services and CLI layers
- [ ] No critical defects in core HTTP/auth handling

### Adoption Criteria

- [ ] assess/* skills can call easel via Bash instead of MCP tools
- [ ] `easel --help` documents all available commands
- [ ] Setup requires only `uv pip install -e .` and a Canvas API token
