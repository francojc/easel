# Development Project Progress

**Project:** easel
**Status:** Phase 2 - Courses
**Last Updated:** 2026-02-22

## Current Status Overview

### Development Phase

- **Current Phase:** Phase 2 - Courses (Proving Ground)
- **Phase Progress:** 0% complete
- **Overall Project Progress:** ~30% complete (Phases 0-1 done)

### Recent Accomplishments

- Phase 0 complete: pyproject.toml, src/easel/ package structure,
  Typer app skeleton, async bridge, output formatting, CanvasError
- Phase 1 complete: Config (pydantic-settings), CanvasClient (httpx
  async with pagination and 429 retry), CourseCache (bidirectional
  code/ID mapping), EaselContext (lazy init), --test and --config
  callbacks wired to real implementations, 27 tests passing, ruff clean

### Active Work

- [ ] Implement courses service (list, details, enrollments)
- [ ] Implement courses CLI sub-commands
- [ ] Service tests with mocked CanvasClient
- [ ] CLI tests with mocked services

## Milestone Tracking

### Completed Milestones

- [x] Phase 0: Scaffolding complete -- `easel --help` works
- [x] Phase 1: Core layer -- config, client, cache tested (27 tests)

### Upcoming Milestones

- [ ] Phase 2: Courses -- first end-to-end service + CLI + tests
- [ ] Phase 3: Assignments + rubrics + grading

### At-Risk Milestones

(none)

## Build and Test Status

### Build Health

- **Last Successful Build:** 2026-02-22 (`uv sync` + `uv run easel --help`)
- **Build Warnings:** None

### Test Results

- **Unit Tests:** 27 passing (config: 4, client: 11, cache: 9, smoke: 3)
- **Integration Tests:** n/a
- **Test Coverage:** Not yet measured

### Open Defects

- **Critical:** 0
- **High:** 0
- **Medium:** 0
- **Low:** 0

## Feature Progress

### Completed Features

- [x] Typer CLI app with global options (--version, --format, --test, --config)
- [x] Async bridge decorator (`_async.py`)
- [x] Output formatting: table, json, plain (`_output.py`)
- [x] CanvasError exception class
- [x] Config via pydantic-settings (env vars, validation)
- [x] CanvasClient (httpx async, pagination, 429 retry, form data)
- [x] CourseCache (bidirectional code/ID mapping, smart resolution)
- [x] EaselContext (lazy init of config, client, cache)
- [x] --test and --config callbacks (real implementations)

### In Progress

- [ ] Courses service + CLI commands - Phase 2, 0% complete

### Planned

- [ ] Courses commands - Phase 2
- [ ] Assignments + rubrics + grading - Phase 3
- [ ] Assessment workflow - Phase 4
- [ ] Remaining entities (student, modules, etc.) - Phase 5
- [ ] Polish (shell completion, docs) - Phase 6

### Deferred or Cut

(none)

## Technical Debt

### Known Debt

(none -- greenfield project)

### Recently Resolved

(none)

## Dependency Status

### External Dependencies

- **httpx:** async HTTP client for Canvas API
- **typer:** CLI framework with rich integration
- **pydantic / pydantic-settings:** config and data validation
- **rich:** terminal output formatting (tables, panels)
- **ruff:** linting and formatting (dev dependency)
- **pytest / pytest-asyncio:** testing (dev dependency)

### Pending Updates

(none -- dependencies not yet pinned)

## Challenges and Blockers

### Current Blockers

(none)

### Resolved Challenges

- httpx mock transport for client tests: used custom
  `AsyncBaseTransport` subclass instead of `respx` library
- Pagination test hung because URL string matching was fragile;
  switched to parsing `request.url.params` dict directly

### Lessons Learned

- Mock httpx at transport level, not with monkeypatching — cleaner
  and tests actual request construction
- Parse URL params from the request object, not string matching

## Next Steps

### Immediate Actions (Next Session)

- [ ] Implement courses service: list_courses(), get_course(),
      get_enrollments()
- [ ] Implement courses CLI sub-app: `easel courses list`,
      `easel courses show <id>`, `easel courses enrollments <id>`
- [ ] Service tests mocking CanvasClient
- [ ] CLI tests mocking service functions with CliRunner
- [ ] Live smoke test against Canvas API

### Medium-term Goals (Next Few Sessions)

- [ ] Assignments, rubrics, grading services (Phase 3)
- [ ] Assessment workflow (Phase 4)

### Decisions Needed

(none)

## Release Planning

### Next Release

- **Version:** 0.1.0
- **Target Date:** TBD
- **Included Features:** Scaffolding + core + courses (Phases 0-2)
- **Release Blockers:** All Phase 0-2 tasks

### Release History

| Version | Date | Key Changes |
|---------|------|-------------|
| (none)  |      |             |
