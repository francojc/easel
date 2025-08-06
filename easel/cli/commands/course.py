"""Course commands for Easel CLI."""

import asyncio
from typing import Optional, List

import click

from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient
from easel.api.exceptions import CanvasAPIError
from easel.config.exceptions import ConfigError
from easel.output.factory import FormatterFactory
from easel.output.columns import parse_include_columns
from ..context import pass_context, EaselContext
from ..error_handlers import with_error_handling


@click.group()
def course() -> None:
    """Course management commands."""
    pass


@course.command()
@click.option(
    "-a", "--active",
    is_flag=True,
    help="Show only active courses",
)
@click.option(
    "--include",
    help="Additional data to include. Common values: total_students, teachers, term, syllabus_body, sections, favorites. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    help="Output format (overrides global format)",
)
@pass_context
@with_error_handling
def list(
    ctx: EaselContext,
    active: bool,
    include: str,
    columns: tuple[str, ...],
    format: str = None,
) -> None:
    """List courses for the current user."""
    # Load configuration
    if not ctx.config_manager:
        raise ConfigError("Configuration manager not initialized")

    config = ctx.config_manager.load_config()
    if not config.canvas.api_token:
        raise ConfigError(
            "No API token found. Run 'easel config init' to set up authentication."
        )

    # Set up API client
    auth = CanvasAuth(config.canvas.api_token)

    async def fetch_courses():
        async with CanvasClient(config.canvas.url, auth) as client:
            # Determine state filter
            state = ["available"] if active else None

            # Convert include string to list (handle comma-separated values)
            include_list = (
                [item.strip() for item in include.split(",")] if include else None
            )

            response = await client.get_courses(
                include=include_list,
                state=state,
            )

            # Collect all courses by handling pagination
            courses = response.items
            while response.has_next_page():
                next_response = await client._make_request(
                    "GET", url=response.get_next_page_url()
                )
                next_data = next_response.json()
                from easel.api.models import Course

                next_courses = [Course(**course_data) for course_data in next_data]
                courses.extend(next_courses)

                # Update pagination info for next iteration
                from easel.api.pagination import PaginatedResponse

                response = PaginatedResponse.from_response(next_response, next_courses)

            return courses

    # Run async operation
    courses = asyncio.run(fetch_courses())

    # Parse display columns
    display_columns = parse_include_columns(columns) if columns else None

    # Format output
    output_format = format if format else ctx.format
    formatter = FormatterFactory.create_formatter(
        output_format, columns=display_columns
    )

    # Convert courses to dictionaries for formatting
    courses_data = [course.model_dump() for course in courses]

    output = formatter.format(courses_data)
    click.echo(output)


@course.command()
@click.argument("course_id", type=int)
@click.option(
    "--include",
    help="Additional data to include. Common values: total_students, teachers, term, syllabus_body, sections, favorites. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    help="Output format (overrides global format)",
)
@pass_context
@with_error_handling
def show(
    ctx: EaselContext,
    course_id: int,
    include: str,
    columns: tuple[str, ...],
    format: str = None,
) -> None:
    """Show detailed information for a specific course."""
    # Load configuration
    if not ctx.config_manager:
        raise ConfigError("Configuration manager not initialized")

    config = ctx.config_manager.load_config()
    if not config.canvas.api_token:
        raise ConfigError(
            "No API token found. Run 'easel config init' to set up authentication."
        )

    # Set up API client
    auth = CanvasAuth(config.canvas.api_token)

    async def fetch_course():
        async with CanvasClient(config.canvas.url, auth) as client:
            # Convert include string to list (handle comma-separated values)
            include_list = (
                [item.strip() for item in include.split(",")] if include else None
            )

            return await client.get_course(
                course_id=course_id,
                include=include_list,
            )

    # Run async operation
    course = asyncio.run(fetch_course())

    # Parse display columns
    display_columns = parse_include_columns(columns) if columns else None

    # Format output
    output_format = format if format else ctx.format
    formatter = FormatterFactory.create_formatter(
        output_format, columns=display_columns
    )

    # Convert course to dictionary for formatting
    course_data = course.model_dump()

    output = formatter.format(course_data)
    click.echo(output)


@course.command()
@click.argument("course_id", type=int)
@click.option(
    "-I", "--include",
    help="Additional data to include. Common values: items, content_details. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    help="Output format (overrides global format)",
)
@pass_context
@with_error_handling
def modules(
    ctx: EaselContext,
    course_id: int,
    include: str,
    columns: tuple[str, ...],
    format: str = None,
) -> None:
    """List modules for a specific course."""
    # Load configuration
    if not ctx.config_manager:
        raise ConfigError("Configuration manager not initialized")

    config = ctx.config_manager.load_config()
    if not config.canvas.api_token:
        raise ConfigError(
            "No API token found. Run 'easel config init' to set up authentication."
        )

    # Set up API client
    auth = CanvasAuth(config.canvas.api_token)

    async def fetch_modules():
        async with CanvasClient(config.canvas.url, auth) as client:
            # Convert include string to list (handle comma-separated values)
            include_list = (
                [item.strip() for item in include.split(",")] if include else None
            )

            response = await client.get_modules(
                course_id=course_id,
                include=include_list,
            )

            # Collect all modules by handling pagination
            modules = response.items
            while response.has_next_page():
                next_response = await client._make_request(
                    "GET", url=response.get_next_page_url()
                )
                next_data = next_response.json()
                from easel.api.models import Module

                next_modules = [Module(**module_data) for module_data in next_data]
                modules.extend(next_modules)

                # Update pagination info for next iteration
                from easel.api.pagination import PaginatedResponse

                response = PaginatedResponse.from_response(next_response, next_modules)

            return modules

    # Run async operation
    modules = asyncio.run(fetch_modules())

    # Parse display columns
    display_columns = parse_include_columns(columns) if columns else None

    # Format output
    output_format = format if format else ctx.format
    formatter = FormatterFactory.create_formatter(
        output_format, columns=display_columns
    )

    # Convert modules to dictionaries for formatting
    modules_data = [module.model_dump() for module in modules]

    output = formatter.format(modules_data)
    click.echo(output)
