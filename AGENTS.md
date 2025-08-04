# Easel Agent Guidelines

This document provides guidelines for AI agents working on the Easel codebase.

## Project Setup & Commands

This project uses Poetry for dependency management.

- **Install dependencies:** `poetry install`
- **Run linters:** `poetry run black . && poetry run flake8 . && poetry run mypy .`
- **Run all tests:** `poetry run pytest`
- **Run a single test:** `poetry run pytest tests/unit/test_course_commands.py::test_list_courses`

## Code Style

- **Formatting:** We use `black` with a line length of 88 characters.
- **Typing:** All functions must have type hints (`mypy` with `disallow_untyped_defs`).
- **Naming:** Use `snake_case` for variables/functions and `PascalCase` for classes.
- **Imports:** Group imports: 1. standard library, 2. third-party, 3. project-specific.
- **Error Handling:** Use custom exceptions from `easel.config.exceptions` and `easel.api.exceptions` where appropriate. Use the `@with_error_handling` decorator for CLI commands.
- **Docstrings:** Use Google-style docstrings.
