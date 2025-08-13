"""Page commands for Easel CLI."""

import asyncio
from pathlib import Path
from typing import Optional

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
def page() -> None:
    """Canvas page management commands."""
    pass


@page.command()
@click.argument("course_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "--include-columns",
    help="Comma-separated list of columns to include in output",
)
@click.option(
    "--published-only",
    is_flag=True,
    help="Show only published pages",
)
@pass_context
@with_error_handling
def list(
    ctx: EaselContext,
    course_id: int,
    output_format: str,
    include_columns: Optional[str],
    published_only: bool,
) -> None:
    """List all Canvas pages for a course.

    Display all pages in a course with their IDs, titles, and metadata.
    Useful for discovering available content and getting page IDs for
    further operations.

    COURSE_ID: The Canvas course ID to list pages from
    """

    async def _list_pages():
        try:
            config = ctx.get_config()
            auth = CanvasAuth(config.token)

            async with CanvasClient(
                config.base_url,
                auth,
                rate_limit=config.rate_limit,
                timeout=config.timeout,
            ) as client:
                # Get course to validate access
                course = await client.get_course(course_id)
                click.echo(f"Listing pages for: {course.name}", err=True)

                # Get pages
                pages = await client.get_pages(course_id)

                if published_only:
                    pages = [p for p in pages if p.published]

                if not pages:
                    click.echo("No pages found", err=True)
                    return

                # Prepare data for output
                pages_data = []
                for page in pages:
                    page_data = {
                        "page_id": page.page_id,
                        "title": page.title,
                        "url": page.url,
                        "published": page.published,
                        "front_page": getattr(page, "front_page", False),
                        "created_at": page.created_at.isoformat()
                        if page.created_at
                        else "",
                        "updated_at": page.updated_at.isoformat()
                        if page.updated_at
                        else "",
                        "editing_roles": getattr(page, "editing_roles", ""),
                        "page_views": getattr(page, "page_views", 0),
                    }
                    pages_data.append(page_data)

                # Apply column filtering if specified
                if include_columns:
                    column_list = parse_include_columns(include_columns)
                    pages_data = [
                        {k: v for k, v in page.items() if k in column_list}
                        for page in pages_data
                    ]

                # Format and output
                formatter = FormatterFactory.create_formatter(output_format)
                output = formatter.format(pages_data)
                click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_list_pages())


@page.command()
@click.argument("course_id", type=int)
@click.argument("page_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "--include-body",
    is_flag=True,
    help="Include page body content in output",
)
@pass_context
@with_error_handling
def show(
    ctx: EaselContext,
    course_id: int,
    page_id: int,
    output_format: str,
    include_body: bool,
) -> None:
    """Show details for a specific page using its ID.

    Display detailed information about a specific Canvas page, including
    metadata and optionally the full content body.

    COURSE_ID: The Canvas course ID containing the page
    PAGE_ID: The Canvas page ID to display
    """

    async def _show_page():
        try:
            config = ctx.get_config()
            auth = CanvasAuth(config.token)

            async with CanvasClient(
                config.base_url,
                auth,
                rate_limit=config.rate_limit,
                timeout=config.timeout,
            ) as client:
                # Get page details
                page = await client.get_page(course_id, page_id)

                # Prepare data for output
                page_data = {
                    "page_id": page.page_id,
                    "title": page.title,
                    "url": page.url,
                    "published": page.published,
                    "front_page": getattr(page, "front_page", False),
                    "created_at": page.created_at.isoformat()
                    if page.created_at
                    else "",
                    "updated_at": page.updated_at.isoformat()
                    if page.updated_at
                    else "",
                    "editing_roles": getattr(page, "editing_roles", ""),
                    "page_views": getattr(page, "page_views", 0),
                }

                if include_body:
                    page_data["body"] = getattr(page, "body", "")

                # Format and output
                if output_format == "table" and include_body:
                    # Special handling for table format with body content
                    click.echo(f"Title: {page.title}")
                    click.echo(f"URL: {page.url}")
                    click.echo(f"Published: {page.published}")
                    click.echo(f"Created: {page.created_at}")
                    click.echo(f"Updated: {page.updated_at}")
                    if include_body:
                        click.echo("\nContent:")
                        click.echo("-" * 50)
                        click.echo(getattr(page, "body", ""))
                else:
                    formatter = FormatterFactory.create_formatter(output_format)
                    output = formatter.format([page_data])
                    click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_show_page())


@page.command()
@click.argument("course_id", type=int)
@click.argument("page_slug")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@pass_context
@with_error_handling
def info(
    ctx: EaselContext,
    course_id: int,
    page_slug: str,
    output_format: str,
) -> None:
    """Display metadata/info for a page using its slug.

    Retrieve additional metadata about a page using its URL slug rather
    than numeric ID. Useful when you know the page URL but not the ID.

    COURSE_ID: The Canvas course ID containing the page
    PAGE_SLUG: The page URL slug (e.g., 'course-syllabus')
    """

    async def _page_info():
        try:
            config = ctx.get_config()
            auth = CanvasAuth(config.token)

            async with CanvasClient(
                config.base_url,
                auth,
                rate_limit=config.rate_limit,
                timeout=config.timeout,
            ) as client:
                # Get page by slug
                page = await client.get_page_by_slug(course_id, page_slug)

                # Prepare metadata
                page_info = {
                    "page_id": page.page_id,
                    "title": page.title,
                    "url": page.url,
                    "slug": page_slug,
                    "published": page.published,
                    "front_page": getattr(page, "front_page", False),
                    "created_at": page.created_at.isoformat()
                    if page.created_at
                    else "",
                    "updated_at": page.updated_at.isoformat()
                    if page.updated_at
                    else "",
                    "last_revised_at": getattr(page, "last_revised_at", ""),
                    "editing_roles": getattr(page, "editing_roles", ""),
                    "page_views": getattr(page, "page_views", 0),
                    "word_count": len(getattr(page, "body", "").split())
                    if hasattr(page, "body")
                    else 0,
                }

                # Format and output
                formatter = FormatterFactory.create_formatter(output_format)
                output = formatter.format([page_info])
                click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_page_info())


@page.command()
@click.argument("course_id", type=int)
@click.argument("page_slug")
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["html", "markdown"]),
    default="html",
    help="Export format",
)
@click.option(
    "--output",
    "output_file",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--all",
    "export_all",
    is_flag=True,
    help="Export all pages in the course (ignores page_slug when used)",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Output directory for bulk export (used with --all)",
)
@pass_context
@with_error_handling
def export(
    ctx: EaselContext,
    course_id: int,
    page_slug: str,
    export_format: str,
    output_file: Optional[str],
    export_all: bool,
    output_dir: Optional[str],
) -> None:
    """Export Canvas page content to HTML or Markdown.

    Export a single page's content or all pages in a course to the specified
    format. Useful for creating backups, documentation, or migrating content.

    COURSE_ID: The Canvas course ID containing the page(s)
    PAGE_SLUG: The page URL slug to export (ignored if --all is used)
    """

    async def _export_pages():
        try:
            config = ctx.get_config()
            auth = CanvasAuth(config.token)

            async with CanvasClient(
                config.base_url,
                auth,
                rate_limit=config.rate_limit,
                timeout=config.timeout,
            ) as client:
                if export_all:
                    # Export all pages
                    if not output_dir:
                        output_dir_path = Path("./exported_pages")
                    else:
                        output_dir_path = Path(output_dir)

                    output_dir_path.mkdir(exist_ok=True)

                    # Get all pages
                    pages = await client.get_pages(course_id)

                    if not pages:
                        click.echo("No pages found to export", err=True)
                        return

                    click.echo(
                        f"Exporting {len(pages)} pages to {output_dir_path}", err=True
                    )

                    with click.progressbar(pages, label="Exporting pages") as page_bar:
                        for page in page_bar:
                            if hasattr(page, "body") and page.body:
                                content = page.body

                                # Convert to markdown if requested
                                if export_format == "markdown":
                                    content = _html_to_markdown(content)

                                # Create safe filename
                                safe_title = "".join(
                                    c
                                    for c in page.title
                                    if c.isalnum() or c in (" ", "-", "_")
                                ).rstrip()
                                filename = f"{safe_title}.{export_format}"
                                filepath = output_dir_path / filename

                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(content)

                    click.echo(
                        f"Exported {len(pages)} pages to {output_dir_path}", err=True
                    )

                else:
                    # Export single page
                    page = await client.get_page_by_slug(course_id, page_slug)

                    if not hasattr(page, "body") or not page.body:
                        click.echo("Page has no content to export", err=True)
                        return

                    content = page.body

                    # Convert to markdown if requested
                    if export_format == "markdown":
                        content = _html_to_markdown(content)

                    # Output to file or stdout
                    if output_file:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(content)
                        click.echo(f"Page exported to {output_file}", err=True)
                    else:
                        click.echo(content)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_export_pages())


def _html_to_markdown(html_content: str) -> str:
    """Convert HTML content to Markdown format.

    Basic HTML to Markdown conversion for Canvas page content.
    This is a simple implementation that handles common HTML tags.
    """
    import re

    # Simple HTML to Markdown conversions
    content = html_content

    # Headers
    content = re.sub(
        r"<h1[^>]*>(.*?)</h1>", r"# \1", content, flags=re.IGNORECASE | re.DOTALL
    )
    content = re.sub(
        r"<h2[^>]*>(.*?)</h2>", r"## \1", content, flags=re.IGNORECASE | re.DOTALL
    )
    content = re.sub(
        r"<h3[^>]*>(.*?)</h3>", r"### \1", content, flags=re.IGNORECASE | re.DOTALL
    )
    content = re.sub(
        r"<h4[^>]*>(.*?)</h4>", r"#### \1", content, flags=re.IGNORECASE | re.DOTALL
    )

    # Bold and italic
    content = re.sub(
        r"<strong[^>]*>(.*?)</strong>",
        r"**\1**",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    content = re.sub(
        r"<b[^>]*>(.*?)</b>", r"**\1**", content, flags=re.IGNORECASE | re.DOTALL
    )
    content = re.sub(
        r"<em[^>]*>(.*?)</em>", r"*\1*", content, flags=re.IGNORECASE | re.DOTALL
    )
    content = re.sub(
        r"<i[^>]*>(.*?)</i>", r"*\1*", content, flags=re.IGNORECASE | re.DOTALL
    )

    # Links
    content = re.sub(
        r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
        r"[\2](\1)",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Lists
    content = re.sub(r"<ul[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"</ul>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<ol[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"</ol>", "", content, flags=re.IGNORECASE)
    content = re.sub(
        r"<li[^>]*>(.*?)</li>", r"- \1", content, flags=re.IGNORECASE | re.DOTALL
    )

    # Paragraphs
    content = re.sub(
        r"<p[^>]*>(.*?)</p>", r"\1\n\n", content, flags=re.IGNORECASE | re.DOTALL
    )

    # Line breaks
    content = re.sub(r"<br[^>]*>", "\n", content, flags=re.IGNORECASE)

    # Remove remaining HTML tags
    content = re.sub(r"<[^>]+>", "", content)

    # Clean up whitespace
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
    content = content.strip()

    return content
