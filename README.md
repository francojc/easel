# `easel` - A CLI for the Canvas LMS API

A standalone CLI for the Canvas LMS API. Provides full coverage of
Canvas operations as terminal commands, usable in scripts, pipelines,
and Claude Code skills.

## Motivation

The [canvas-mcp](https://github.com/francojc/canvas-mcp) project
exposes Canvas LMS operations through FastMCP. The core business logic
(HTTP client, config, caching, utilities) has zero MCP coupling. easel
extracts that logic into a shared service layer and wraps it with a
Typer CLI, making Canvas operations available from any terminal.

## Architecture

```
Typer CLI <- commands <- services (async business logic) <- core
```

- **Core** (`core/`) -- HTTP client, config, caching, and utility
  functions.
- **Services** (`services/`) -- Async functions that call the Canvas
  API and return structured data. No formatting, no framework
  awareness. Raises `CanvasError` on failure.
- **CLI** (`cli/`) -- Typer commands that call services, format output,
  and handle errors with exit codes and stderr.

## CLI usage

Commands are organized by Canvas entity:

```
easel courses list [--concluded]
easel courses details <course>
easel assignments list <course> [--current-only]
easel assignments create <course> --name "HW1" --points 100
easel student upcoming [--days 14]
easel student grades [--course <course>]
easel discussions list <course>
easel modules list <course>
easel rubrics details <course> <assignment-id>
easel grading setup <course> <assignment-id>
```

### Output formats

All commands support `--format` with three modes:

- `table` (default) -- aligned columns for terminal use
- `json` -- machine-readable, for piping and scripting
- `plain` -- simple key-value pairs

### Global options

```
easel --version
easel --test          # test Canvas API connection
easel --config        # show current configuration
```

## Installation

Requires Python 3.11+.

```sh
uv pip install -e .
```

This installs the `easel` command.

## Development

```sh
uv sync
```

### Running tests

```sh
uv run pytest tests/
```

Tests are organized in two layers:

- `tests/services/` -- service functions with mocked API calls
- `tests/cli/` -- CLI integration tests with `typer.testing.CliRunner`

### Implementation roadmap

The extraction follows an incremental, one-category-per-PR approach:

1. **Scaffolding** -- service and CLI directory structure, Typer app
   skeleton, async bridging, output formatting
2. **Courses** -- proving ground for the full extract-wrap-test cycle
3. **Remaining categories** -- assignments, student, modules,
   discussions, rubrics, pages, messaging, peer reviews, files, grading
4. **Cleanup** -- remove test hacks, update documentation, add shell
   completion

## License

See [LICENSE](LICENSE).
