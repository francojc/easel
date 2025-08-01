# Easel CLI

Python CLI tool for Canvas LMS API access.

## Installation

```bash
pip install easel
```

## Quick Start

```bash
# Initialize configuration
easel init

# Validate setup
easel doctor

# List courses
easel course list
```

## Development

```bash
# Install dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run flake8
poetry run mypy easel

# Install pre-commit hooks
poetry run pre-commit install
```

## Documentation

See the `specs/` directory for detailed specifications and the `adr/` directory for architectural decisions.

## License

MIT