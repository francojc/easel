"""User commands for Easel CLI."""

import asyncio
from typing import Optional

import click

from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient
from easel.api.exceptions import CanvasAPIError
from easel.output.factory import FormatterFactory
from easel.output.columns import parse_include_columns
from ..context import pass_context, EaselContext


@click.group()
def user() -> None:
    """User management commands."""
    pass


@user.command()
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@pass_context
def profile(ctx: EaselContext, columns: tuple[str, ...]) -> None:
    """Show current user profile information."""
    try:
        # Load configuration
        if not ctx.config_manager:
            raise click.ClickException("Configuration manager not initialized")

        config = ctx.config_manager.load_config()
        if not config.canvas.api_token:
            raise click.ClickException(
                "No API token found. Run 'easel config init' to set up authentication."
            )

        # Set up API client
        auth = CanvasAuth(config.canvas.api_token)

        async def fetch_user():
            async with CanvasClient(config.canvas.url, auth) as client:
                return await client.verify_connection()

        # Run async operation
        user = asyncio.run(fetch_user())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert user to dictionary for formatting
        user_data = user.model_dump()

        output = formatter.format(user_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")


@user.command()
@click.option(
    "--role",
    type=click.Choice(["student", "teacher", "ta", "observer", "designer"]),
    help="Filter courses by enrollment role",
)
@click.option(
    "--state",
    type=click.Choice(["active", "invited", "completed"]),
    help="Filter courses by enrollment state",
)
@click.option(
    "--include",
    help="Common values: total_students, term. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@pass_context
def courses(
    ctx: EaselContext,
    role: Optional[str],
    state: Optional[str],
    include: str,
    columns: tuple[str, ...],
) -> None:
    """List courses for the current user."""
    try:
        # Load configuration
        if not ctx.config_manager:
            raise click.ClickException("Configuration manager not initialized")

        config = ctx.config_manager.load_config()
        if not config.canvas.api_token:
            raise click.ClickException(
                "No API token found. Run 'easel config init' to set up authentication."
            )

        # Set up API client
        auth = CanvasAuth(config.canvas.api_token)

        async def fetch_courses():
            async with CanvasClient(config.canvas.url, auth) as client:
                # Convert include string to list (handle comma-separated values)
                include_list = (
                    [item.strip() for item in include.split(",")] if include else None
                )

                # Build state filter
                state_filter = None
                if state:
                    state_filter = [state]

                response = await client.get_courses(
                    include=include_list,
                    state=state_filter,
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

                    response = PaginatedResponse.from_response(
                        next_response, next_courses
                    )

                # Filter by role if specified
                if role:
                    filtered_courses = []
                    for course in courses:
                        if course.enrollments:
                            for enrollment in course.enrollments:
                                if enrollment.get("role") == role:
                                    filtered_courses.append(course)
                                    break
                    courses = filtered_courses

                return courses

        # Run async operation
        courses = asyncio.run(fetch_courses())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert courses to dictionaries for formatting
        courses_data = [course.model_dump() for course in courses]

        output = formatter.format(courses_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")


@user.command()
@click.argument("course_id", type=int)
@click.option(
    "--role",
    type=click.Choice(["student", "teacher", "ta", "observer", "designer"]),
    help="Filter users by enrollment role",
)
@click.option(
    "--include",
    help="Common values: enrollments, avatar_url. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@pass_context
def roster(
    ctx: EaselContext,
    course_id: int,
    role: Optional[str],
    include: str,
    columns: tuple[str, ...],
) -> None:
    """List users enrolled in a specific course."""
    try:
        # Load configuration
        if not ctx.config_manager:
            raise click.ClickException("Configuration manager not initialized")

        config = ctx.config_manager.load_config()
        if not config.canvas.api_token:
            raise click.ClickException(
                "No API token found. Run 'easel config init' to set up authentication."
            )

        # Set up API client
        auth = CanvasAuth(config.canvas.api_token)

        async def fetch_users():
            async with CanvasClient(config.canvas.url, auth) as client:
                # Build enrollment type filter
                enrollment_type = None
                if role:
                    # Map role to Canvas enrollment types
                    role_mapping = {
                        "student": "StudentEnrollment",
                        "teacher": "TeacherEnrollment",
                        "ta": "TaEnrollment",
                        "observer": "ObserverEnrollment",
                        "designer": "DesignerEnrollment",
                    }
                    enrollment_type = [role_mapping.get(role, role)]

                # Convert include string to list (handle comma-separated values)
                include_list = (
                    [item.strip() for item in include.split(",")] if include else None
                )

                response = await client.get_users(
                    course_id=course_id,
                    enrollment_type=enrollment_type,
                    include=include_list,
                )

                # Collect all users by handling pagination
                users = response.items
                while response.has_next_page():
                    next_response = await client._make_request(
                        "GET", url=response.get_next_page_url()
                    )
                    next_data = next_response.json()
                    from easel.api.models import User

                    next_users = [User(**user_data) for user_data in next_data]
                    users.extend(next_users)

                    # Update pagination info for next iteration
                    from easel.api.pagination import PaginatedResponse

                    response = PaginatedResponse.from_response(
                        next_response, next_users
                    )

                return users

        # Run async operation
        users = asyncio.run(fetch_users())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert users to dictionaries for formatting
        users_data = [user.model_dump() for user in users]

        output = formatter.format(users_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")
