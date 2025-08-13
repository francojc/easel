"""Content discovery commands for Easel CLI."""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

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
def content() -> None:
    """Content discovery and analysis commands."""
    pass


@content.command()
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
    "--module-filter",
    help="Filter by module name (partial match)",
)
@click.option(
    "--content-type",
    type=click.Choice(
        ["all", "files", "pages", "assignments", "discussions", "quizzes"]
    ),
    default="all",
    help="Filter by content type",
)
@click.option(
    "--published-only",
    is_flag=True,
    help="Show only published content",
)
@pass_context
@with_error_handling
def list(
    ctx: EaselContext,
    course_id: int,
    output_format: str,
    include_columns: Optional[str],
    module_filter: Optional[str],
    content_type: str,
    published_only: bool,
) -> None:
    """Create content inventory for a course.

    Analyze and list all content in a course including files, pages,
    assignments, discussions, and quizzes. Provides metadata about
    content organization, accessibility, and usage.

    COURSE_ID: The Canvas course ID to analyze
    """

    async def _list_content():
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
                click.echo(f"Analyzing content for: {course.name}", err=True)

                content_items = []

                # Get modules for organization context
                modules = await client.get_modules(course_id)
                module_dict = {m.id: m.name for m in modules}

                if module_filter:
                    modules = [
                        m for m in modules if module_filter.lower() in m.name.lower()
                    ]

                # Process different content types
                if content_type in ["all", "files"]:
                    files = await client.get_files(course_id)
                    for file in files:
                        # Handle raw file data from API
                        if published_only and not file.get("published", True):
                            continue

                        content_items.append(
                            {
                                "type": "file",
                                "id": file.get("id"),
                                "name": file.get("display_name")
                                or file.get("filename", ""),
                                "size": file.get("size", 0),
                                "content_type": file.get("content-type", ""),
                                "created_at": file.get("created_at", ""),
                                "updated_at": file.get("updated_at", ""),
                                "published": file.get("published", True),
                                "folder": file.get("folder_id", ""),
                                "download_url": file.get("url", ""),
                            }
                        )

                if content_type in ["all", "pages"]:
                    pages = await client.get_pages(course_id)
                    for page in pages:
                        if published_only and not page.published:
                            continue

                        content_items.append(
                            {
                                "type": "page",
                                "id": page.page_id,
                                "name": page.title,
                                "size": len(getattr(page, "body") or ""),
                                "content_type": "text/html",
                                "created_at": page.created_at.isoformat()
                                if page.created_at
                                else "",
                                "updated_at": page.updated_at.isoformat()
                                if page.updated_at
                                else "",
                                "published": page.published,
                                "folder": "",
                                "download_url": f"/courses/{course_id}/pages/{page.url}",
                            }
                        )

                if content_type in ["all", "assignments"]:
                    assignments = await client.get_assignments(course_id)
                    for assignment in assignments:
                        if published_only and not assignment.published:
                            continue

                        content_items.append(
                            {
                                "type": "assignment",
                                "id": assignment.id,
                                "name": assignment.name,
                                "size": len(getattr(assignment, "description", "")),
                                "content_type": "text/html",
                                "created_at": assignment.created_at.isoformat()
                                if assignment.created_at
                                else "",
                                "updated_at": assignment.updated_at.isoformat()
                                if assignment.updated_at
                                else "",
                                "published": assignment.published,
                                "folder": "",
                                "download_url": f"/courses/{course_id}/assignments/{assignment.id}",
                            }
                        )

                if content_type in ["all", "discussions"]:
                    discussions = await client.get_discussions(course_id)
                    for discussion in discussions:
                        if published_only and not discussion.published:
                            continue

                        content_items.append(
                            {
                                "type": "discussion",
                                "id": discussion.id,
                                "name": discussion.title,
                                "size": len(getattr(discussion, "message", "")),
                                "content_type": "text/html",
                                "created_at": discussion.posted_at.isoformat()
                                if discussion.posted_at
                                else "",
                                "updated_at": discussion.last_reply_at.isoformat()
                                if discussion.last_reply_at
                                else "",
                                "published": discussion.published,
                                "folder": "",
                                "download_url": f"/courses/{course_id}/discussion_topics/{discussion.id}",
                            }
                        )

                if not content_items:
                    click.echo("No content found", err=True)
                    return

                # Apply column filtering if specified
                if include_columns:
                    column_list = parse_include_columns(include_columns)
                    content_items = [
                        {k: v for k, v in item.items() if k in column_list}
                        for item in content_items
                    ]

                # Sort by type and name
                content_items.sort(key=lambda x: (x["type"], x["name"]))

                # Format and output
                formatter = FormatterFactory.create_formatter(output_format)
                output = formatter.format(content_items)
                click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_list_content())


@content.command()
@click.argument("course_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "--include-files",
    is_flag=True,
    help="Include file-level analysis in the report",
)
@pass_context
@with_error_handling
def analytics(
    ctx: EaselContext,
    course_id: int,
    output_format: str,
    include_files: bool,
) -> None:
    """Generate content analytics and usage statistics.

    Analyze content usage patterns, accessibility, organization,
    and provide insights for content management and optimization.

    COURSE_ID: The Canvas course ID to analyze
    """

    async def _content_analytics():
        try:
            config = ctx.get_config()
            auth = CanvasAuth(config.token)

            async with CanvasClient(
                config.base_url,
                auth,
                rate_limit=config.rate_limit,
                timeout=config.timeout,
            ) as client:
                # Get course details
                course = await client.get_course(course_id)
                click.echo(f"Analyzing content for: {course.name}", err=True)

                # Initialize analytics data
                analytics = {
                    "course_name": course.name,
                    "content_summary": {},
                    "organization_analysis": {},
                    "accessibility_analysis": {},
                    "usage_patterns": {},
                }

                # Get all content types
                with click.progressbar(label="Analyzing content", length=6) as bar:
                    # Files
                    files = await client.get_files(course_id)
                    bar.update(1)

                    # Pages
                    pages = await client.get_pages(course_id)
                    bar.update(1)

                    # Assignments
                    assignments = await client.get_assignments(course_id)
                    bar.update(1)

                    # Discussions
                    discussions = await client.get_discussions(course_id)
                    bar.update(1)

                    # Modules
                    modules = await client.get_modules(course_id)
                    bar.update(1)

                    bar.update(1)  # Complete

                # Content summary
                total_file_size = sum(f.get("size", 0) for f in files)

                analytics["content_summary"] = {
                    "total_files": len(files),
                    "total_pages": len(pages),
                    "total_assignments": len(assignments),
                    "total_discussions": len(discussions),
                    "total_modules": len(modules),
                    "total_file_size_mb": round(total_file_size / (1024 * 1024), 2)
                    if total_file_size
                    else 0,
                }

                # File type analysis
                file_types = {}
                for file in files:
                    content_type = file.get("content-type", "unknown")
                    if content_type not in file_types:
                        file_types[content_type] = {"count": 0, "size": 0}
                    file_types[content_type]["count"] += 1
                    file_types[content_type]["size"] += file.get("size", 0)

                analytics["file_type_distribution"] = file_types

                # Organization analysis
                published_content = {
                    "pages": len([p for p in pages if p.published]),
                    "assignments": len([a for a in assignments if a.published]),
                    "discussions": len([d for d in discussions if d.published]),
                }

                analytics["organization_analysis"] = {
                    "modules_count": len(modules),
                    "published_content": published_content,
                    "unpublished_content": {
                        "pages": len(pages) - published_content["pages"],
                        "assignments": len(assignments)
                        - published_content["assignments"],
                        "discussions": len(discussions)
                        - published_content["discussions"],
                    },
                }

                # Content accessibility analysis
                large_files = [
                    f for f in files if f.get("size", 0) > 10 * 1024 * 1024
                ]  # > 10MB

                analytics["accessibility_analysis"] = {
                    "large_files_count": len(large_files),
                    "large_files_total_size_mb": round(
                        sum(f.get("size", 0) for f in large_files) / (1024 * 1024), 2
                    ),
                    "empty_pages": len(
                        [p for p in pages if not getattr(p, "body", "").strip()]
                    ),
                    "empty_assignments": len(
                        [
                            a
                            for a in assignments
                            if not getattr(a, "description", "").strip()
                        ]
                    ),
                }

                # Include detailed file analysis if requested
                if include_files:
                    analytics["file_details"] = [
                        {
                            "name": f.get("display_name") or f.get("filename", ""),
                            "size_mb": round(f.get("size", 0) / (1024 * 1024), 2),
                            "type": f.get("content-type", "unknown"),
                            "created": f.get("created_at", ""),
                        }
                        for f in sorted(
                            files, key=lambda x: x.get("size", 0), reverse=True
                        )[:20]
                    ]

                # Format output
                if output_format == "table":
                    output = _format_content_analytics_table(analytics)
                    click.echo(output)
                else:
                    formatter = FormatterFactory.create_formatter(output_format)
                    output = formatter.format([analytics])
                    click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_content_analytics())


def _format_content_analytics_table(data: Dict[str, Any]) -> str:
    """Format content analytics as a readable table."""
    import io

    output = io.StringIO()

    # Course overview
    output.write(f"Course: {data['course_name']}\n\n")

    # Content summary
    summary = data["content_summary"]
    output.write("Content Summary:\n")
    output.write(
        f"  Files: {summary['total_files']} ({summary['total_file_size_mb']} MB)\n"
    )
    output.write(f"  Pages: {summary['total_pages']}\n")
    output.write(f"  Assignments: {summary['total_assignments']}\n")
    output.write(f"  Discussions: {summary['total_discussions']}\n")
    output.write(f"  Modules: {summary['total_modules']}\n\n")

    # File type distribution
    if "file_type_distribution" in data:
        output.write("File Type Distribution:\n")
        for file_type, stats in data["file_type_distribution"].items():
            size_mb = round(stats["size"] / (1024 * 1024), 2)
            output.write(f"  {file_type}: {stats['count']} files ({size_mb} MB)\n")
        output.write("\n")

    # Organization analysis
    org = data["organization_analysis"]
    output.write("Organization Analysis:\n")
    output.write(f"  Modules: {org['modules_count']}\n")
    output.write("  Published Content:\n")
    for content_type, count in org["published_content"].items():
        output.write(f"    {content_type.title()}: {count}\n")
    output.write("  Unpublished Content:\n")
    for content_type, count in org["unpublished_content"].items():
        output.write(f"    {content_type.title()}: {count}\n")
    output.write("\n")

    # Accessibility analysis
    access = data["accessibility_analysis"]
    output.write("Accessibility Analysis:\n")
    output.write(
        f"  Large Files (>10MB): {access['large_files_count']} ({access['large_files_total_size_mb']} MB)\n"
    )
    output.write(f"  Empty Pages: {access['empty_pages']}\n")
    output.write(f"  Empty Assignments: {access['empty_assignments']}\n")

    # File details if included
    if "file_details" in data:
        output.write("\nLargest Files:\n")
        for file_detail in data["file_details"][:10]:
            output.write(
                f"  {file_detail['name']}: {file_detail['size_mb']} MB ({file_detail['type']})\n"
            )

    return output.getvalue()
