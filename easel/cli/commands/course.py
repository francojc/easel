"""Course commands for Easel CLI."""

import asyncio
from typing import Optional, List

import click

from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient
from easel.api.exceptions import CanvasAPIError
from easel.config.exceptions import ConfigError
from easel.output.factory import FormatterFactory
from ..context import pass_context, EaselContext
from ..error_handlers import with_error_handling
from ..main import cli


@cli.group()
def course() -> None:
    """Course management commands."""
    pass


@course.command()
@click.option(
    "--active",
    is_flag=True,
    help="Show only active courses",
)
@click.option(
    "--include",
    multiple=True,
    help="Additional data to include (e.g., total_students)",
)
@pass_context
@with_error_handling
def list(ctx: EaselContext, active: bool, include: tuple[str, ...]) -> None:
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
            
            # Convert include tuple to list
            include_list = list(include) if include else None
            
            response = await client.get_courses(
                include=include_list,
                state=state,
            )
            
            # Collect all courses by handling pagination
            courses = response.data
            while response.has_next_page:
                next_response = await client._make_request("GET", url=response.next_page_url)
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
    
    # Format output
    formatter = FormatterFactory.create_formatter(ctx.format)
    
    # Convert courses to dictionaries for formatting
    courses_data = [course.model_dump() for course in courses]
    
    output = formatter.format(courses_data)
    click.echo(output)


@course.command()
@click.argument("course_id", type=int)
@click.option(
    "--include",
    multiple=True,
    help="Additional data to include (e.g., syllabus_body, term)",
)
@pass_context
@with_error_handling
def show(ctx: EaselContext, course_id: int, include: tuple[str, ...]) -> None:
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
            # Convert include tuple to list
            include_list = list(include) if include else None
            
            return await client.get_course(
                course_id=course_id,
                include=include_list,
            )

    # Run async operation
    course = asyncio.run(fetch_course())
    
    # Format output
    formatter = FormatterFactory.create_formatter(ctx.format)
    
    # Convert course to dictionary for formatting
    course_data = course.model_dump()
    
    output = formatter.format(course_data)
    click.echo(output)


@course.command()
@click.argument("course_id", type=int)
@click.option(
    "--include",
    multiple=True,
    help="Additional data to include (e.g., items)",
)
@pass_context
@with_error_handling
def modules(ctx: EaselContext, course_id: int, include: tuple[str, ...]) -> None:
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
            # Convert include tuple to list
            include_list = list(include) if include else None
            
            response = await client.get_modules(
                course_id=course_id,
                include=include_list,
            )
            
            # Collect all modules by handling pagination
            modules = response.data
            while response.has_next_page:
                next_response = await client._make_request("GET", url=response.next_page_url)
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
    
    # Format output
    formatter = FormatterFactory.create_formatter(ctx.format)
    
    # Convert modules to dictionaries for formatting
    modules_data = [module.model_dump() for module in modules]
    
    output = formatter.format(modules_data)
    click.echo(output)