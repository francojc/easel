# ADR 001: CLI Framework Selection

**Status:** Accepted
**Date:** 2025-07-31
**Deciders:** Jerid Francom, Development Team
**Technical Story:** Foundation for Easel CLI command structure and user interface

## Context and Problem Statement

Easel needs a robust command-line interface framework to handle complex command hierarchies, argument parsing, help generation, and user interaction. The CLI will serve as the primary interface for Canvas LMS automation and must provide excellent developer and user experience.

The framework must support:

- Hierarchical commands (e.g., `easel course list`, `easel assignment show <id>`)
- Rich help system with auto-generation
- Shell completion support
- Input validation and error handling
- Plugin architecture for extensibility
- Professional-grade user experience

## Decision Drivers

- **User Experience:** Intuitive command structure and helpful error messages
- **Developer Productivity:** Easy to extend with new commands and features
- **Community Standards:** Widely adopted in Python ecosystem
- **Shell Integration:** Excellent completion and piping support
- **Documentation:** Auto-generated help that stays in sync with code
- **Maintenance:** Active development and long-term support

## Considered Options

- **Click** - Composable command line interface toolkit
- **argparse** - Python standard library argument parser
- **Typer** - Modern CLI framework based on type hints
- **Fire** - Automatic CLI generation from Python objects

## Decision Outcome

**Chosen option:** "Click"

**Rationale:** Click provides the best balance of power, flexibility, and ecosystem support for our needs. It offers excellent command composition, built-in shell completion, and is the de facto standard for professional Python CLI tools.

### Positive Consequences

- Rich command grouping and hierarchy support
- Excellent shell completion out of the box
- Extensive ecosystem of plugins and extensions
- Battle-tested in production environments (used by Flask, Databricks CLI, etc.)
- Excellent documentation and community support
- Built-in support for configuration files and environment variables

### Negative Consequences

- Slightly more verbose than Typer for simple commands
- Learning curve for advanced features like custom parameter types
- Additional dependency (though minimal impact)

## Pros and Cons of the Options

### Click

**Description:** Composable command line interface toolkit with rich features

**Pros:**

- Excellent command grouping and nesting support
- Built-in shell completion for bash, zsh, and fish
- Rich parameter types and validation
- Excellent help system with automatic generation
- Strong ecosystem and plugin support
- Used by major Python projects (high confidence)
- Support for complex CLI patterns (commands, groups, contexts)

**Cons:**

- More verbose than some alternatives
- Decorator-heavy approach may be unfamiliar to some developers
- Can be complex for very simple CLI needs

### argparse

**Description:** Python standard library argument parser

**Pros:**

- No external dependencies
- Part of Python standard library
- Familiar to most Python developers
- Lightweight and fast

**Cons:**

- Very verbose for complex command hierarchies
- Poor support for shell completion
- Manual help formatting required
- Limited built-in validation options
- Difficult to create plugin architectures

### Typer

**Description:** Modern CLI framework based on type hints and FastAPI patterns

**Pros:**

- Very concise syntax using type hints
- Automatic validation based on types
- Modern Python practices (3.6+ features)
- Good documentation and examples

**Cons:**

- Relatively new (less battle-tested)
- Smaller ecosystem compared to Click
- Type hint dependency may limit Python version support
- Less flexible for complex custom behaviors

### Fire

**Description:** Automatic CLI generation from Python objects

**Pros:**

- Zero boilerplate - automatic CLI from functions/classes
- Very rapid prototyping
- Simple to get started

**Cons:**

- Limited control over CLI structure and presentation
- Poor help formatting and user experience
- Not suitable for professional CLI tools
- Limited validation and error handling options

## Implementation Notes

### Command Structure

```python
import click

@click.group()
@click.option('--config', type=click.Path(), help='Configuration file path')
@click.option('--format', type=click.Choice(['table', 'json', 'csv', 'yaml']))
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, format, verbose):
    """Easel CLI - Canvas LMS automation tool"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['format'] = format
    ctx.obj['verbose'] = verbose

@cli.group()
def course():
    """Course management commands"""
    pass

@course.command()
@click.option('--active', is_flag=True, help='Show only active courses')
@click.pass_context
def list(ctx, active):
    """List courses"""
    # Implementation here
    pass
```

### Shell Completion Setup

```python
# Built-in Click completion
@click.command()
@click.option('--install-completion', type=click.Choice(['bash', 'zsh', 'fish']))
def cli(install_completion):
    if install_completion:
        # Install completion for specified shell
        click.echo(f"Installing completion for {install_completion}")
```

### Plugin Architecture Foundation

```python
# Entry points in setup.py/pyproject.toml for plugins
[tool.poetry.plugins."easel.commands"]
custom_command = "easel_plugin.commands:custom_command"

# Plugin discovery
def load_plugins():
    for entry_point in pkg_resources.iter_entry_points('easel.commands'):
        command = entry_point.load()
        cli.add_command(command)
```

## Links

- [Click Documentation](https://click.palletsprojects.com/)
- [Click GitHub Repository](https://github.com/pallets/click)
- [Shell Completion Guide](https://click.palletsprojects.com/en/8.1.x/shell-completion/)
- [Advanced Patterns](https://click.palletsprojects.com/en/8.1.x/advanced/)
