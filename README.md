# `easel` - A CLI for the Canvas LMS API

A standalone CLI for the Canvas LMS API, extracted from the
[canvas-mcp](https://github.com/francojc/canvas-mcp) project. Provides
full coverage of Canvas operations as terminal commands, usable in
scripts, pipelines, and Claude Code skills — independent of the MCP
server.

## Motivation

The canvas-mcp project exposes 84 tools through FastMCP. The core
business logic (HTTP client, config, caching, utilities) has zero MCP
coupling, but it is currently only accessible through the MCP protocol.
easel extracts that logic into a shared service layer and wraps it with
a Typer CLI, so the same operations work from any terminal.

## Architecture

The project follows a three-layer design:

```
FastMCP  <- thin MCP wrappers  <- services (async business logic) <- core
Typer CLI <- thin CLI commands  <- services (async business logic) <- core
```

- **Core** (`core/`) -- HTTP client, config, caching, date and
  anonymization utilities. Unchanged from canvas-mcp.
- **Services** (`services/`) -- Shared async functions that call the
  Canvas API and return structured data. No formatting, no framework
  awareness. Raises `CanvasError` on failure.
- **CLI** (`cli/`) -- Typer commands that call services, format output,
  and handle errors with exit codes and stderr.
- **Tools** (`tools/`) -- MCP tool wrappers that call the same services,
  format output as strings for LLM consumption.

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
pip install -e .
```

This installs the `easel` CLI entry point alongside the existing
`canvas-mcp-server`.

## Development

### Running tests

```sh
pytest tests/
```

Tests are organized in three layers:

- `tests/services/` -- service functions with mocked API calls
- `tests/cli/` -- CLI integration tests with `typer.testing.CliRunner`
- `tests/tools/` -- thin MCP wrapper verification

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
