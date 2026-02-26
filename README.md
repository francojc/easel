# easel

A terminal-native CLI for the Canvas LMS API. Manage courses,
assignments, grading, and content from the command line — or use it as
a backend for Claude Code skill commands.

## Installation

Requires Python 3.11+.

```sh
uv pip install -e .
```

This installs the `easel` command. You also need two environment
variables:

```sh
export CANVAS_API_KEY="your-canvas-api-token"
export CANVAS_BASE_URL="https://your-institution.instructure.com"
```

The `/api/v1` path is appended automatically.

## Quick start

```sh
easel --test                        # verify API connection
easel courses list                  # list your courses
easel assignments list IS505        # list assignments (course code or ID)
easel grading submissions IS505 42  # list submissions for assignment 42
```

All commands accept `--format` with three modes:

- `table` (default) — aligned columns for terminal reading
- `json` — machine-readable, for piping and scripting
- `plain` — simple key-value pairs

## Commands

### courses

```
easel courses list [--concluded]
easel courses show <course>
easel courses enrollments <course>
```

### assignments

```
easel assignments list <course>
easel assignments show <course> <assignment-id>
easel assignments create <course> <name> [--points N] [--due ISO] [--publish]
easel assignments update <course> <assignment-id> [--name ...] [--points N]
easel assignments rubrics <course>
easel assignments rubric <course> <assignment-id>
```

### grading

```
easel grading submissions <course> <assignment-id> [--anonymize]
easel grading show <course> <assignment-id> <user-id> [--anonymize]
easel grading submit <course> <assignment-id> <user-id> <grade> [--comment ...]
easel grading submit-rubric <course> <assignment-id> <user-id> <json> [--comment ...]
```

### assess

```
easel assess setup <course> <assignment-id> [--exclude-graded] [--anonymize] [--format json]
easel assess load <file>
easel assess update <file> <user-id> [--rubric-json ...] [--approved]
easel assess submit <file> <course> <assignment-id> [--confirm]
```

The `assess` sub-app manages the full assessment workflow: fetch
assignment data, build an assessment JSON file, update individual
scores, and submit approved grades back to Canvas. Submit runs in
dry-run mode by default — pass `--confirm` to post grades.

### Anonymizing student data

Commands that return student information support `--anonymize` to strip
personally identifiable information before output. When enabled,
`user_name` and `user_email` are replaced with empty strings. The
numeric `user_id` (Canvas's opaque integer) is retained — it carries no
identifying information outside the institution and is required for
grade submission round-tripping.

Affected commands: `assess setup`, `grading submissions`, `grading show`.

```sh
easel assess setup IS505 42 --anonymize -o assessment.json
easel grading submissions IS505 42 --anonymize --format json
```

This is opt-in. Without `--anonymize`, output includes full names and
emails as returned by the Canvas API.

### modules

```
easel modules list <course> [--items] [--search ...]
easel modules show <course> <module-id>
easel modules create <course> <name> [--position N] [--publish]
easel modules update <course> <module-id> [--name ...] [--publish/--unpublish]
easel modules delete <course> <module-id>
```

### pages

```
easel pages list <course> [--search ...] [--sort title|created_at|updated_at]
easel pages show <course> <page-url>
easel pages create <course> <title> [--body ...] [--publish]
easel pages update <course> <page-url> [--title ...] [--body ...]
easel pages delete <course> <page-url>
```

### discussions

```
easel discussions list <course> [--announcements]
easel discussions show <course> <topic-id>
easel discussions create <course> <title> [--message ...] [--announcement] [--publish]
easel discussions update <course> <topic-id> [--title ...] [--message ...]
```

### config

```
easel config init [--base .]
easel config global
easel config show
```

`config init` creates `.claude/course_parameters.yaml` in the current
repo with interactive prompts. `config global` manages shared defaults
at `~/.config/easel/config.toml`. `config show` displays the merged
view of both, annotated by source.

### commands

```
easel commands install [--overwrite]
```

Copies the bundled assess skill commands into
`.claude/commands/assess/` in the current repo.

### Global options

```
easel --version          # show version
easel --test             # test Canvas API connection
easel --config           # show current configuration
easel --install-completion   # install shell completion
easel --show-completion      # show completion script
```

## Architecture

```
CLI (Typer) -> services (async) -> core (HTTP client, config, cache)
```

- **Core** — `CanvasClient` (httpx async with pagination and 429
  retry), `Config` (pydantic-settings), `CourseCache` (bidirectional
  code/ID mapping), config file helpers (TOML/YAML).
- **Services** — Async functions per Canvas entity. Accept a
  `CanvasClient`, return dicts/lists, raise `CanvasError` on failure.
- **CLI** — Typer commands that bridge async via decorator, format
  output through `format_output()`, and exit with appropriate codes.

Course arguments accept both course codes (e.g., `IS505`) and numeric
Canvas IDs. The `CourseCache` resolves either form transparently.

## Extending with AI

easel is designed to work as a backend for Claude Code skill commands.
Any command that accepts `--format json` can be called from a skill
via Bash, and the structured output parsed for downstream use.

### Skill commands

Skill commands are Markdown files in `.claude/commands/` that Claude
Code executes as multi-step workflows. easel ships four assessment
skills that automate rubric-based grading:

1. `/assess:setup` — fetch assignment data from Canvas and build an
   assessment JSON file with rubric structure and student submissions
2. `/assess:ai-pass` — evaluate each submission against the rubric
   using Claude, writing scores and feedback into the assessment file
3. `/assess:refine` — normalize scores across the cohort using
   0.5-point increments, adjusting for consistency
4. `/assess:submit` — post approved grades and comments back to Canvas

### Installing skill commands

```sh
easel commands install
```

This copies the four assess skills into your repo's
`.claude/commands/assess/` directory. Once installed, invoke them from
Claude Code with `/assess:setup`, `/assess:ai-pass`, etc.

### Writing custom skills

Any script or skill can call easel. A minimal example that lists
ungraded submissions:

```bash
uv run easel grading submissions IS505 42 --format json \
  | jq '[.[] | select(.grade == null)]'
```

Skills can chain multiple easel calls — fetch data with `--format
json`, process it, and submit results back. The assess pipeline is a
worked example of this pattern: setup fetches data, the AI pass
writes to a local file, and submit pushes grades to Canvas.

### Configuration for skills

Skills that use easel for grading need course context. Run
`easel config init` to create `.claude/course_parameters.yaml` with
fields like course code, feedback language, and formality level. The
assess skills read this file to configure their behavior.

## Development

```sh
uv sync                         # install dependencies
uv run easel --help             # verify install
uv run pytest tests/            # run tests (234 passing)
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
```

Tests are organized in two layers:

- `tests/services/` — service tests that mock `CanvasClient`
- `tests/cli/` — CLI tests that mock service functions and use
  `typer.testing.CliRunner`

## License

See [LICENSE](LICENSE).
