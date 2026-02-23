# easel - Canvas LMS CLI

## Commands

- Build: `uv sync`
- Run: `uv run easel <command>`
- Test: `uv run pytest tests/`
- Lint: `uv run ruff check src/ tests/`
- Format: `uv run ruff format src/ tests/`

## File structure

```
src/easel/
├── core/         # HTTP client, config, caching, date utils
├── services/     # Async business logic per Canvas entity
└── cli/          # Typer commands, async bridging, output formatting

tests/
├── services/     # Service tests — mock at CanvasClient level
└── cli/          # CLI tests — mock at service level, use CliRunner

.claude/commands/assess/   # Skill commands installed via `easel commands install`
```

## Architecture

CLI -> services -> core. Services are async functions that accept a
CanvasClient and return dicts/lists. CLI commands bridge async with
`asyncio.run()`, format output, and handle errors with exit codes.

## Reference repo

canvas-mcp (`~/.local/mcp/canvas-mcp/`) contains the business logic
patterns easel adapts. Reference only -- no runtime dependency.

## Gotchas

- Canvas API uses bracket-notation for rubric assessment form data
  (e.g., `rubric_assessment[criterion_id][points]`). The rubrics
  service must encode these correctly.
- Course identifiers can be codes (e.g., "IS505") or numeric IDs.
  The CourseCache handles bidirectional mapping. Always resolve
  through the cache.
- Never read .env files directly. Canvas API token comes from
  `CANVAS_API_KEY` env var via pydantic-settings. The base URL
  comes from `CANVAS_BASE_URL`; `/api/v1` is appended automatically.
- Async bridging: services are async, Typer callbacks are sync.
  Use the `_async.py` bridge decorator to call services from CLI.
- Output formatting: all commands support `--format` (table/json/plain).
  Use `_output.py`'s `format_output()` for consistent rendering.
