# easel

A command-line interface for the Canvas LMS API. Manage courses,
assignments, grading, and content from the terminal.

easel also serves as a backend for
[Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill
commands, enabling AI-assisted grading workflows via `--format json`.

## Installation

**Requirements:** Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/francojc/easel.git
cd easel
```

Install `easel` to `~/.local/bin/` so it's available system-wide:

```sh
uv tool install -e .
```

The `-e` (editable) flag means changes to the source take effect
immediately without reinstalling. To update after a `git pull`:

```sh
uv tool install -e . --force
```

If you prefer to run from the project directory without a global
install, use `uv run easel` instead (after `uv sync`).

Set two environment variables for Canvas API access:

```sh
export CANVAS_API_KEY="your-canvas-api-token"
export CANVAS_BASE_URL="https://your-institution.instructure.com"
```

The `/api/v1` path is appended automatically. Generate an API token
from your Canvas account settings under "Approved Integrations."

Verify the install and connection:

```sh
easel --version
easel --test
```

## Quick start

```sh
# List your courses
easel courses list

# List assignments for a course (accepts codes or numeric IDs)
easel assignments list --course IS505

# View submissions for an assignment
easel grading submissions --course IS505 42

# Set up course-level config
easel config init
```

All commands accept `--format` (`-f`) with four output modes:

| Mode    | Use case                          |
|---------|-----------------------------------|
| `table` | Aligned columns (default)         |
| `json`  | Machine-readable, for piping      |
| `plain` | Simple key-value pairs            |
| `csv`   | Header + rows, pipe to file/tools |

## Configuration

easel uses two TOML config files. Local values override global.

**Global** (instructor defaults shared across courses):

```
$XDG_CONFIG_HOME/easel/config.toml    # default: ~/.config/easel/config.toml
```

Set up interactively or write defaults without prompting:

```sh
easel config global              # interactive prompts
easel config global --defaults   # write starter config
```

**Local** (per-course settings in the repo root):

```
./easel/config.toml
```

```sh
easel config init                # interactive prompts, pre-fills from global
```

**View merged config:**

```sh
easel config show                # shows each value with [global] or [local] source
```

## Commands

### courses

```
easel courses list [--concluded]
easel courses show [--course COURSE]
easel courses enrollments [--course COURSE]
```

List, inspect, and view enrollments for your courses. The `--course`
option accepts course codes (e.g., `IS505`) or numeric Canvas IDs.
When omitted, falls back to `canvas_course_id` in your config file.

### assignments

```
easel assignments list [--course COURSE]
easel assignments show [--course COURSE] <assignment-id>
easel assignments create [--course COURSE] <name> [--points N] [--due ISO] [--publish]
easel assignments update [--course COURSE] <assignment-id> [--name ...] [--points N]
easel assignments rubrics [--course COURSE]
easel assignments rubric [--course COURSE] <assignment-id>
```

Create, update, list, and inspect assignments. `rubrics` lists all
rubrics for a course; `rubric` shows the detailed rubric for a
specific assignment.

### grading

```
easel grading submissions [--course COURSE] <assignment-id> [--anonymize]
easel grading show [--course COURSE] <assignment-id> <user-id> [--anonymize]
easel grading submit [--course COURSE] <assignment-id> <user-id> <grade> [--comment ...]
easel grading submit-rubric [--course COURSE] <assignment-id> <user-id> <file> [--comment ...]
```

View submissions, inspect individual student work, and post grades.
`submit-rubric` reads rubric criterion scores from a JSON file.

### assess

```
easel assess setup [--course COURSE] <assignment-id> [--exclude-graded] [--anonymize]
easel assess load <file>
easel assess update <file> <user-id> [--rubric-json ...] [--approved]
easel assess submit <file> [--course COURSE] <assignment-id> [--confirm]
```

Full rubric-based assessment workflow: fetch assignment data into a
local JSON file, update individual scores, and submit approved grades
back to Canvas. Submit runs in dry-run mode by default; pass
`--confirm` to post grades.

### modules

```
easel modules list [--course COURSE] [--items] [--search ...]
easel modules show [--course COURSE] <module-id>
easel modules create [--course COURSE] <name> [--position N] [--publish]
easel modules update [--course COURSE] <module-id> [--name ...] [--publish/--unpublish]
easel modules delete [--course COURSE] <module-id>
```

### pages

```
easel pages list [--course COURSE] [--search ...] [--sort title|created_at|updated_at]
easel pages show [--course COURSE] <page-url>
easel pages create [--course COURSE] <title> [--body ...] [--publish]
easel pages update [--course COURSE] <page-url> [--title ...] [--body ...]
easel pages delete [--course COURSE] <page-url>
```

Pages are identified by their URL slug (e.g., `syllabus-spring-2026`).

### discussions

```
easel discussions list [--course COURSE] [--announcements]
easel discussions show [--course COURSE] <topic-id>
easel discussions create [--course COURSE] <title> [--message ...] [--announcement] [--publish]
easel discussions update [--course COURSE] <topic-id> [--title ...] [--message ...]
```

Pass `--announcements` to list only announcements. Use `--announcement`
when creating to post an announcement rather than a discussion topic.

### config

```
easel config init [--base .]
easel config global [--defaults]
easel config show
```

See [Configuration](#configuration) above for details.

### commands

```
easel commands install [--overwrite] [--local]
```

Copies bundled Claude Code skill commands (assess, assignments,
content, course, discuss, grading) into `~/.claude/commands/`.
Pass `--local` to install into the current repo's
`.claude/commands/` instead. See [Skill commands](#skill-commands)
below.

### Global options

```
easel --version             # show version
easel --test                # test Canvas API connection
easel --config              # show API URL and token (masked)
easel --format json <cmd>   # JSON output for any command
easel --install-completion  # install shell tab-completion
```

## Anonymizing student data

Commands that return student information support `--anonymize` to
strip personally identifiable information. When enabled, `user_name`
and `user_email` are replaced with empty strings. The numeric
`user_id` is retained for grade submission round-tripping.

Affected commands: `assess setup`, `grading submissions`, `grading show`.

```sh
easel assess setup --course IS505 42 --anonymize --format json
easel grading submissions --course IS505 42 --anonymize
```

This is opt-in. Without `--anonymize`, output includes full names and
emails as returned by the Canvas API.

## Skill commands

easel ships Claude Code skill commands that automate multi-step
instructor workflows. Install them with:

```sh
easel commands install
```

This copies Markdown command files into `~/.claude/commands/` across
six groups:

| Group         | Commands                                      |
|---------------|-----------------------------------------------|
| `assess`      | setup, ai-pass, refine, submit                |
| `assignments` | create                                        |
| `content`     | publish                                       |
| `course`      | setup, overview                               |
| `discuss`     | announce                                      |
| `grading`     | overview                                      |

Once installed, invoke them from Claude Code (e.g., `/assess:setup`,
`/course:overview`). Skills call easel via `--format json` and parse
the structured output for downstream processing.

### Writing custom skills

Any script or Claude Code skill can call easel. A minimal example
that lists ungraded submissions:

```sh
easel grading submissions --course IS505 42 --format json \
  | jq '[.[] | select(.grade == null)]'
```

Skills that need course context (feedback language, formality, etc.)
read from `./easel/config.toml`. Run `easel config init` to set it up.

## Development

```sh
uv sync                         # install dependencies
uv run easel --help             # verify install
uv run pytest tests/            # run tests
uv run ruff check src/ tests/   # lint
uv run ruff format src/ tests/  # format
```

### Architecture

```
CLI (Typer) -> services (async) -> core (HTTP client, config, cache)
```

- **Core** -- `CanvasClient` (httpx async, pagination, 429 retry),
  `Config` (pydantic-settings), `CourseCache` (bidirectional code/ID
  mapping), config file helpers (TOML).
- **Services** -- Async functions per Canvas entity. Accept a
  `CanvasClient`, return dicts/lists, raise `CanvasError` on failure.
- **CLI** -- Typer commands that bridge async via decorator, format
  output through `format_output()`, and exit with appropriate codes.

### Tests

Tests are organized in two layers:

- `tests/services/` -- mock at the `CanvasClient` transport level
- `tests/cli/` -- mock at the service function level, use
  `typer.testing.CliRunner`

## License

See [LICENSE](LICENSE).
