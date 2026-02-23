# Development Project Progress

**Project:** easel
**Status:** Phase 6 - Polish (IN PROGRESS)
**Last Updated:** 2026-02-22

## Current Status Overview

### Development Phase

- **Current Phase:** Phase 6 - Polish (IN PROGRESS)
- **Phase Progress:** ~40% complete (skills migrated, commands install done)
- **Overall Project Progress:** ~93% complete (Phases 0-5 done, Phase 6 underway)

### Recent Accomplishments

- Phase 0 complete: pyproject.toml, src/easel/ package structure,
  Typer app skeleton, async bridge, output formatting, CanvasError
- Phase 1 complete: Config (pydantic-settings), CanvasClient (httpx
  async with pagination and 429 retry), CourseCache (bidirectional
  code/ID mapping), EaselContext (lazy init), --test and --config
  callbacks wired to real implementations, 27 tests passing, ruff clean
- Phase 2 complete: Courses service (list_courses, get_course,
  get_enrollments), courses CLI sub-app (list, show, enrollments),
  service tests mocking CanvasClient, CLI tests mocking services,
  44 tests passing, ruff clean
- Phase 3 complete: Assignments service (list, get, create, update),
  rubrics service (list, get, bracket-notation form builder), grading
  service (submissions, get, submit grade, submit rubric grade),
  assignments CLI (list, show, create, update, rubrics, rubric),
  grading CLI (submissions, show, submit, submit-rubric),
  99 tests passing, ruff clean
- Phase 4 complete: Assessment service (fetch assignment+rubric, fetch
  submissions with content, build/load/save/update assessment JSON,
  stats, submit approved assessments to Canvas), assessment CLI
  (setup, load, update, submit with dry-run), 133 tests passing,
  ruff clean
- Phase 5 complete: Modules service (list, get, create, update,
  delete), pages service (list, get, create, update, delete with
  slug-based IDs), discussions service (list, get, create, update
  with announcement support), CLI sub-apps for all three, HTML
  stripping in pages and discussions, 210 tests passing, ruff clean

### Active Work

- Phase 6 (polish) in progress: `commands install` CLI added, assess
  skill commands migrated from MCP to easel CLI

## Milestone Tracking

### Completed Milestones

- [x] Phase 0: Scaffolding complete -- `easel --help` works
- [x] Phase 1: Core layer -- config, client, cache tested (27 tests)
- [x] Phase 2: Courses -- service + CLI + tests (44 tests total)
- [x] Phase 3: Assignments + rubrics + grading (99 tests total)
- [x] Phase 4: Assessment workflow (133 tests total)
- [x] Phase 5: Modules, pages, discussions (210 tests total)

### Upcoming Milestones

- [ ] Phase 6: Polish (shell completion, docs) -- in progress
- [ ] 0.1.0 release

### At-Risk Milestones

(none)

## Build and Test Status

### Build Health

- **Last Successful Build:** 2026-02-22 (`uv sync` + `uv run easel --help`)
- **Build Warnings:** None

### Test Results

- **Unit Tests:** 210 passing
  - core: config 4, client 11, cache 9
  - services: courses 9, assignments 14, rubrics 8, grading 10,
    assessments 22, modules 14, pages 15, discussions 15
  - cli: courses 8, assignments 13, grading 10, assessments 12,
    modules 11, pages 12, discussions 12
  - smoke: 3
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
- [x] Courses service: list_courses, get_course, get_enrollments
- [x] Courses CLI: `easel courses list`, `show`, `enrollments`
- [x] Assignments service: list, get, create, update (with HTML stripping)
- [x] Rubrics service: list, get, bracket-notation form data builder
- [x] Grading service: list submissions, get submission, submit grade,
  submit rubric grade
- [x] Assignments CLI: `easel assignments list|show|create|update|rubrics|rubric`
- [x] Grading CLI: `easel grading submissions|show|submit|submit-rubric`
- [x] Assessment service: fetch assignment+rubric, fetch submissions
  with content, build/load/save/update JSON, stats, submit to Canvas
- [x] Assessment CLI: `easel assess setup|load|update|submit`
- [x] Commands CLI: `easel commands install` (copies .claude/commands/assess/*.md)
- [x] Assess skill commands migrated from MCP to easel CLI (setup, ai-pass, refine, submit)
- [x] Modules service: list, get, create, update, delete
- [x] Modules CLI: `easel modules list|show|create|update|delete`
- [x] Pages service: list, get, create, update, delete (slug-based IDs)
- [x] Pages CLI: `easel pages list|show|create|update|delete`
- [x] Discussions service: list, get, create, update (with announcements)
- [x] Discussions CLI: `easel discussions list|show|create|update`

### In Progress

- [ ] Phase 6: Polish and release prep

### Planned

- [ ] `easel config` sub-app (init, global, show) -- repo-level
  course_parameters.yaml setup with global config inheritance
- [ ] Shell completion support
- [ ] README with "Extending with AI" section (skills, custom
  workflows, assess/* pipeline walkthrough)
- [ ] Final documentation pass

### Deferred or Cut

- Student commands (deferred -- not needed for instructor workflows)

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

- Mock httpx at transport level, not with monkeypatching -- cleaner
  and tests actual request construction
- Parse URL params from the request object, not string matching
- For CLI tests, mock at the service function level and patch
  get_context to avoid needing real config/credentials
- AsyncMock works well for service functions called from
  async_command-bridged CLI commands

## Next Steps

### Immediate Actions (Next Session)

- [ ] Live smoke test against Canvas API (all commands)
- [ ] Live smoke test of migrated assess/* skills against a real assignment
- [ ] Implement `easel config` sub-app (init/global/show)
- [ ] Shell completion support
- [ ] Write README with "Extending with AI" section
- [ ] Final documentation pass

### Medium-term Goals (Next Few Sessions)

- [ ] 0.1.0 release

### Decisions Needed

(none)

## Release Planning

### Next Release

- **Version:** 0.1.0
- **Target Date:** TBD
- **Included Features:** Scaffolding + core + courses + assignments +
  rubrics + grading + assessment workflow + modules + pages +
  discussions (Phases 0-5)
- **Release Blockers:** Live smoke test, config sub-app, shell
  completion, README/documentation

### Release History

| Version | Date | Key Changes |
|---------|------|-------------|
| (none)  |      |             |
