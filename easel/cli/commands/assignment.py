"""Assignment commands for Easel CLI."""

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
def assignment() -> None:
    """Assignment management commands."""
    pass


@assignment.command()
@click.argument("course_id", type=int)
@click.option(
    "-I", "--include",
    help="Common values: submission, needs_grading_count. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@pass_context
def list(
    ctx: EaselContext,
    course_id: int,
    include: str,
    columns: tuple[str, ...],
) -> None:
    """List assignments for a course."""
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

        async def fetch_assignments():
            async with CanvasClient(config.canvas.url, auth) as client:
                # Convert include string to list (handle comma-separated values)
                include_list = (
                    [item.strip() for item in include.split(",")] if include else None
                )

                response = await client.get_assignments(
                    course_id=course_id,
                    include=include_list,
                )

                # Collect all assignments by handling pagination
                assignments = response.items
                while response.has_next_page():
                    next_response = await client._make_request(
                        "GET", url=response.get_next_page_url()
                    )
                    next_data = next_response.json()
                    from easel.api.models import Assignment

                    next_assignments = [
                        Assignment(**assignment_data) for assignment_data in next_data
                    ]
                    assignments.extend(next_assignments)

                    # Update pagination info for next iteration
                    from easel.api.pagination import PaginatedResponse

                    response = PaginatedResponse.from_response(
                        next_response, next_assignments
                    )

                return assignments

        # Run async operation
        assignments = asyncio.run(fetch_assignments())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert assignments to dictionaries for formatting
        assignments_data = [assignment.model_dump() for assignment in assignments]

        output = formatter.format(assignments_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")


@assignment.command()
@click.argument("course_id", type=int)
@click.argument("assignment_id", type=int)
@click.option(
    "-I", "--include",
    help="Common values: submission. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@pass_context
def show(
    ctx: EaselContext,
    course_id: int,
    assignment_id: int,
    include: str,
    columns: tuple[str, ...],
) -> None:
    """Show detailed information for a specific assignment."""
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

        async def fetch_assignment():
            async with CanvasClient(config.canvas.url, auth) as client:
                # Convert include string to list (handle comma-separated values)
                include_list = (
                    [item.strip() for item in include.split(",")] if include else None
                )

                return await client.get_assignment(
                    course_id=course_id,
                    assignment_id=assignment_id,
                    include=include_list,
                )

        # Run async operation
        assignment = asyncio.run(fetch_assignment())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert assignment to dictionary for formatting
        assignment_data = assignment.model_dump()

        output = formatter.format(assignment_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")


@assignment.command()
@click.argument("course_id", type=int)
@click.argument("assignment_id", type=int)
@click.option(
    "-I", "--include",
    help="Common values: user, submission_history. Use comma-separated values for multiple items.",
)
@click.option(
    "--columns",
    multiple=True,
    help="Display specific columns (use 'all' for all columns)",
)
@click.option(
    "-s", "--status",
    type=click.Choice(["submitted", "unsubmitted", "graded", "pending_review"]),
    help="Filter submissions by status",
)
@pass_context
def submissions(
    ctx: EaselContext,
    course_id: int,
    assignment_id: int,
    include: str,
    columns: tuple[str, ...],
    status: Optional[str],
) -> None:
    """List submissions for a specific assignment."""
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

        async def fetch_submissions():
            async with CanvasClient(config.canvas.url, auth) as client:
                # Convert include string to list (handle comma-separated values)
                include_list = (
                    [item.strip() for item in include.split(",")] if include else None
                )

                response = await client.get_submissions(
                    course_id=course_id,
                    assignment_id=assignment_id,
                    include=include_list,
                )

                # Collect all submissions by handling pagination
                submissions = response.items
                while response.has_next_page():
                    next_response = await client._make_request(
                        "GET", url=response.get_next_page_url()
                    )
                    next_data = next_response.json()
                    from easel.api.models import Submission

                    next_submissions = [
                        Submission(**submission_data) for submission_data in next_data
                    ]
                    submissions.extend(next_submissions)

                    # Update pagination info for next iteration
                    from easel.api.pagination import PaginatedResponse

                    response = PaginatedResponse.from_response(
                        next_response, next_submissions
                    )

                # Filter by status if specified
                if status:
                    if status == "submitted":
                        submissions = [
                            s for s in submissions if s.submitted_at is not None
                        ]
                    elif status == "unsubmitted":
                        submissions = [s for s in submissions if s.submitted_at is None]
                    elif status == "graded":
                        submissions = [s for s in submissions if s.score is not None]
                    elif status == "pending_review":
                        submissions = [
                            s
                            for s in submissions
                            if s.workflow_state == "pending_review"
                        ]

                return submissions

        # Run async operation
        submissions = asyncio.run(fetch_submissions())

        # Parse display columns
        display_columns = parse_include_columns(columns) if columns else None

        # Format output
        formatter = FormatterFactory.create_formatter(
            ctx.format, columns=display_columns
        )

        # Convert submissions to dictionaries for formatting
        submissions_data = [submission.model_dump() for submission in submissions]

        output = formatter.format(submissions_data)
        click.echo(output)

    except CanvasAPIError as e:
        raise click.ClickException(f"Canvas API error: {e}")
    except Exception as e:
        if ctx.verbose:
            raise
        raise click.ClickException(f"Error: {e}")
