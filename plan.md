# Easel CLI: Implementation Plan

## Context

The `easel` project is a standalone CLI for the Canvas LMS API. The
canvas-mcp project serves only as a reference for business logic and
API patterns — easel has no runtime dependency on it. The CLI works
in terminals, scripts, and pipelines, and is designed so Claude Code
skills can call it via Bash with `--format json` to replace MCP tool
calls. Package management uses `uv` throughout.

Current state: git repo with only `README.md` committed. Everything
below needs to be created.

## Architecture

```
Typer CLI  ->  services (async)  ->  core (HTTP, config, cache)
```

- **Core** — class-based `CanvasClient` (httpx), `Config`
  (pydantic-settings), `CourseCache`. Adapted from canvas-mcp's
  `core/` but simplified: no anonymization, no audit logging, no
  sandbox config. Raises exceptions instead of returning error dicts.
- **Services** — async functions that accept a client, return
  dicts/lists, raise `CanvasError`. No formatting, no CLI awareness.
- **CLI** — Typer commands that bridge async, call services, format
  output. Errors go to stderr with non-zero exit codes.

## Phases

### Phase 0: Scaffolding

Create project skeleton and verify `easel --help` works.

**Create:**

- `pyproject.toml` — hatchling build, `easel` entry point, deps:
  httpx, typer[all], pydantic, pydantic-settings, python-dotenv,
  python-dateutil, rich. Dev deps: pytest, pytest-asyncio, ruff.
  Python >=3.11. `[tool.hatch.build.targets.wheel] packages = ["src/easel"]`
- `src/easel/__init__.py` — `__version__ = "0.1.0"`
- `src/easel/core/__init__.py`
- `src/easel/services/__init__.py` — `CanvasError` exception class
- `src/easel/cli/__init__.py`
- `src/easel/cli/app.py` — main Typer app with `--version`, `--test`,
  `--config`, `--format` global callback
- `src/easel/cli/_async.py` — `asyncio.run()` bridge decorator
- `src/easel/cli/_output.py` — `OutputFormat` enum, `format_output()`
  rendering to json/table/plain via rich
- `tests/__init__.py`
- `tests/conftest.py` — shared fixtures

**Update:**

- `README.md` — remove `tests/tools/` reference (two test layers:
  `tests/services/` and `tests/cli/`)

**Verify:** `uv sync && uv run easel --help`

### Phase 1: Core layer

Adapt from canvas-mcp `core/` (reference only, not imported).

**Create:**

- `src/easel/core/config.py` — `pydantic-settings` `BaseSettings`
  subclass. Fields: `canvas_api_token`, `canvas_api_url`
  (default `https://canvas.illinois.edu/api/v1`), `api_timeout` (30),
  `debug` (false). `validate()` method checks token/URL.
  Ref: `canvas-mcp/src/canvas_mcp/core/config.py`
- `src/easel/core/client.py` — `CanvasClient` class wrapping
  `httpx.AsyncClient`. Methods: `request()`, `get_paginated()`,
  `test_connection()`, `close()`. Retry with backoff on 429.
  Raises `CanvasError` on HTTP errors.
  Ref: `canvas-mcp/src/canvas_mcp/core/client.py`
- `src/easel/core/cache.py` — `CourseCache` class with bidirectional
  code/ID mapping, lazy refresh.
  Ref: `canvas-mcp/src/canvas_mcp/core/cache.py`
- `src/easel/core/dates.py` — date formatting utilities, copied and
  simplified from canvas-mcp.
- `src/easel/cli/_context.py` — lazy initialization of `Config`,
  `CanvasClient`, `CourseCache`. Provides `get_client()`,
  `get_cache()`, `get_config()` for CLI commands.
- `tests/services/` directory (empty `__init__.py`)
- `tests/cli/` directory (empty `__init__.py`)

**Verify:** `uv run pytest tests/` (config and client unit tests)

### Phase 2: Courses (proving ground)

Establishes the full service -> CLI -> test pattern.

**Create:**

- `src/easel/services/courses.py` — `list_courses()`,
  `get_course_details()`, `get_course_enrollments()`.
  Ref: `canvas-mcp/src/canvas_mcp/tools/courses.py`
- `src/easel/cli/courses.py` — Typer sub-app registered on main app.
  Commands: `list`, `details`, `enrollments`.
- `tests/services/test_courses.py` — mock at `CanvasClient` level
- `tests/cli/test_courses.py` — `typer.testing.CliRunner`, mock at
  service level

**Verify:**

```
uv run easel courses list
uv run easel courses list --format json
uv run easel courses details <course-code>
uv run pytest tests/
```

### Phase 3: Assignments + rubrics + grading

Priority group — these are the commands the assess/* skills need.

**Create (one service + CLI file per category):**

- `services/assignments.py` + `cli/assignments.py` —
  `list`, `details`, `create`, `update`, `submissions`.
  Ref: `canvas-mcp/src/canvas_mcp/tools/assignments.py`
- `services/rubrics.py` + `cli/rubrics.py` —
  `list`, `details`. Includes `build_rubric_assessment_form_data`
  helper for Canvas bracket-notation encoding.
  Ref: `canvas-mcp/src/canvas_mcp/tools/rubrics.py`
- `services/grading.py` + `cli/grading.py` —
  `submissions` (with text extraction), `submit-grades`.
  Ref: `canvas-mcp/src/canvas_mcp/tools/grading.py`
- Tests for each in `tests/services/` and `tests/cli/`

**Verify:** `uv run pytest tests/ && uv run easel assignments list <course> --format json`

### Phase 4: Assessment workflow commands

Local JSON assessment file management — the commands that replace
`load_assessment_file`, `review_assessment`, and
`submit_reviewed_assessments` MCP tools.

**Create:**

- `services/assessments.py` + `cli/assessments.py` — commands:
  - `load <path>` — validate JSON structure, return summary/data
  - `update <path> <user-id> --data '{...}' [--reviewed] [--approved]`
  - `submit <path> --course <id> --assignment <id> [--dry-run]`
  Ref: `canvas-mcp/src/canvas_mcp/tools/grading.py` lines 540-982
- Tests for each

**Verify:**

```
uv run easel assessments load .claude/assessments/test.json --format json
uv run pytest tests/
```

### Phase 5: Remaining entity groups

Lower priority. Each follows the Phase 2 pattern.

- `student` — `upcoming`, `grades`, `todo`
- `modules` — `list`, `details`, `create`
- `discussions` — `list`, `entries`, `reply`
- `pages` — `list`, `details`, `create`, `update`
- `messaging` — `send`
- `files` — `list`, `upload`, `download`

Each gets a service file, CLI file, and tests.

### Phase 6: Polish

- `CLAUDE.md` — build/test commands, file structure, gotchas
- `flake.nix` + `.envrc` — Python 3.11 + uv via nix
- Wire `easel --test` to `CanvasClient.test_connection()`
- Wire `easel --config` to display non-secret config values
- Shell completion: `easel --install-completion`

## Key reference files (canvas-mcp)

- `src/canvas_mcp/core/client.py` — HTTP retry/pagination logic
- `src/canvas_mcp/core/config.py` — env var pattern to simplify
- `src/canvas_mcp/core/cache.py` — course code/ID cache
- `src/canvas_mcp/tools/courses.py` — template for service extraction
- `src/canvas_mcp/tools/grading.py` — assessment workflow logic
- `src/canvas_mcp/tools/rubrics.py` — rubric form-encoding helpers

## Verification (end-to-end)

After all phases:

```
uv sync
uv run easel --help                              # all sub-apps listed
uv run easel --test                              # API connectivity
uv run easel courses list                        # table output
uv run easel courses list --format json          # JSON output
uv run easel assignments list <course>           # entity commands work
uv run easel assessments load <path> --format json  # assessment workflow
uv run pytest tests/                             # all tests pass
```
