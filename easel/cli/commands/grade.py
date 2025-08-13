"""Grade commands for Easel CLI."""

import asyncio
import csv
import io
import statistics
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
def grade() -> None:
    """Grade management and analytics commands."""
    pass


@grade.command()
@click.argument("course_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    default="csv",
    help="Output format",
)
@click.option(
    "--output",
    "output_file",
    type=click.Path(),
    help="Output file path (default: stdout)",
)
@click.option(
    "--assignment-group",
    help="Filter by assignment group name",
)
@click.option(
    "--include-columns",
    help="Comma-separated list of columns to include in output",
)
@pass_context
@with_error_handling
def export(
    ctx: EaselContext,
    course_id: int,
    output_format: str,
    output_file: Optional[str],
    assignment_group: Optional[str],
    include_columns: Optional[str],
) -> None:
    """Export grades for a course.

    Export all grades for assignments in a course, with optional filtering
    by assignment group. Supports multiple output formats with Excel-compatible
    CSV as the default.

    COURSE_ID: The Canvas course ID to export grades from
    """

    async def _export_grades():
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
                click.echo(f"Exporting grades for: {course.name}", err=True)

                # Get assignments with filtering
                assignments = await client.get_assignments(course_id)
                
                # Fetch assignment groups and create a mapping
                groups = await client.get_assignment_groups(course_id)
                group_map = {g["id"]: g["name"] for g in groups}
                
                if assignment_group:
                    # Map names to IDs for filtering
                    matching_group_ids = [
                        g["id"]
                        for g in groups
                        if assignment_group.lower() in g["name"].lower()
                    ]
                    if not matching_group_ids:
                        click.echo(f"No assignment group found matching '{assignment_group}'", err=True)
                        return
                    assignments = [
                        a
                        for a in assignments
                        if hasattr(a, "assignment_group_id") and a.assignment_group_id in matching_group_ids
                    ]

                if not assignments:
                    click.echo("No assignments found", err=True)
                    return

                # Get all submissions for all assignments
                grades_data = []

                # Get students enrolled in course
                enrollments = await client.get_enrollments(
                    course_id, enrollment_type="StudentEnrollment"
                )
                # Create user objects from enrollment data
                student_map = {}
                for enrollment in enrollments:
                    user_data = enrollment.get("user", {})
                    if user_data:
                        # Create a simple user-like object
                        user = type(
                            "User",
                            (),
                            {
                                "id": user_data.get("id"),
                                "name": user_data.get("name", ""),
                                "email": user_data.get("email", ""),
                            },
                        )()
                        student_map[user.id] = user

                with click.progressbar(
                    assignments, label="Fetching grades", show_eta=True
                ) as assignment_bar:
                    for assignment in assignment_bar:
                        submissions = await client.get_submissions(
                            course_id, assignment.id
                        )

                        for submission in submissions:
                            if submission.user_id in student_map:
                                student = student_map[submission.user_id]
                                grade_record = {
                                    "student_id": student.id,
                                    "student_name": student.name,
                                    "student_email": getattr(student, "email", ""),
                                    "assignment_id": assignment.id,
                                    "assignment_name": assignment.name,
                                    "assignment_group": group_map.get(assignment.assignment_group_id, ""),
                                    "points_possible": assignment.points_possible,
                                    "score": submission.score,
                                    "grade": submission.grade,
                                    "submission_type": submission.submission_type,
                                    "submitted_at": submission.submitted_at.isoformat()
                                    if submission.submitted_at
                                    else "",
                                    "graded_at": submission.graded_at.isoformat()
                                    if submission.graded_at
                                    else "",
                                    "late": submission.late,
                                    "missing": submission.missing,
                                    "excused": submission.excused,
                                }
                                grades_data.append(grade_record)

                if not grades_data:
                    click.echo("No grade data found", err=True)
                    return

                # Apply column filtering if specified
                if include_columns:
                    column_list = parse_include_columns(include_columns)
                    grades_data = [
                        {k: v for k, v in record.items() if k in column_list}
                        for record in grades_data
                    ]

                # Format and output data
                formatter = FormatterFactory.create_formatter(output_format)

                if output_format == "csv" and output_file:
                    # Special handling for CSV to ensure Excel compatibility
                    with open(
                        output_file, "w", newline="", encoding="utf-8-sig"
                    ) as csvfile:
                        if grades_data:
                            fieldnames = grades_data[0].keys()
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(grades_data)
                    click.echo(f"Grades exported to {output_file}", err=True)
                else:
                    # Use standard formatter
                    output = formatter.format(grades_data)

                    if output_file:
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(output)
                        click.echo(f"Grades exported to {output_file}", err=True)
                    else:
                        click.echo(output)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_export_grades())


@grade.command()
@click.argument("course_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "--export-raw",
    is_flag=True,
    help="Export raw data along with analytics",
)
@pass_context
@with_error_handling
def analytics(
    ctx: EaselContext,
    course_id: int,
    output_format: str,
    export_raw: bool,
) -> None:
    """Generate grade analytics for a course.

    Analyze grade distributions, student performance trends, and assignment
    difficulty to provide actionable insights for educators.

    COURSE_ID: The Canvas course ID to analyze
    """

    async def _grade_analytics():
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
                click.echo(f"Analyzing grades for: {course.name}", err=True)

                # Get assignments and submissions
                assignments = await client.get_assignments(course_id)
                enrollments = await client.get_enrollments(
                    course_id, enrollment_type="StudentEnrollment"
                )

                if not assignments:
                    click.echo("No assignments found for analysis", err=True)
                    return

                # Collect all scores for analysis
                all_scores = []
                assignment_stats = {}
                student_performance = {}

                with click.progressbar(
                    assignments, label="Analyzing assignments", show_eta=True
                ) as assignment_bar:
                    for assignment in assignment_bar:
                        submissions = await client.get_submissions(
                            course_id, assignment.id
                        )

                        # Filter for graded submissions
                        graded_submissions = [
                            s
                            for s in submissions
                            if s.score is not None and not s.excused
                        ]

                        if graded_submissions:
                            scores = [s.score for s in graded_submissions]
                            percentages = [
                                (s.score / assignment.points_possible * 100)
                                if assignment.points_possible > 0
                                else 0
                                for s in graded_submissions
                            ]

                            assignment_stats[assignment.name] = {
                                "points_possible": assignment.points_possible,
                                "submissions_count": len(graded_submissions),
                                "mean_score": statistics.mean(scores),
                                "median_score": statistics.median(scores),
                                "std_dev": statistics.stdev(scores)
                                if len(scores) > 1
                                else 0,
                                "mean_percentage": statistics.mean(percentages),
                                "min_score": min(scores),
                                "max_score": max(scores),
                                "late_submissions": sum(
                                    1 for s in submissions if s.late
                                ),
                                "missing_submissions": sum(
                                    1 for s in submissions if s.missing
                                ),
                            }

                            all_scores.extend(percentages)

                            # Track student performance
                            for submission in graded_submissions:
                                if submission.user_id not in student_performance:
                                    student_performance[submission.user_id] = []

                                percentage = (
                                    (
                                        submission.score
                                        / assignment.points_possible
                                        * 100
                                    )
                                    if assignment.points_possible > 0
                                    else 0
                                )
                                student_performance[submission.user_id].append(
                                    percentage
                                )

                # Calculate overall course statistics
                if all_scores:
                    course_stats = {
                        "course_name": course.name,
                        "total_assignments": len(assignments),
                        "total_students": len(enrollments),
                        "class_average": statistics.mean(all_scores),
                        "class_median": statistics.median(all_scores),
                        "std_deviation": statistics.stdev(all_scores)
                        if len(all_scores) > 1
                        else 0,
                    }

                    # Grade distribution analysis
                    grade_distribution = {
                        "A (90-100%)": len([s for s in all_scores if s >= 90]),
                        "B (80-89%)": len([s for s in all_scores if 80 <= s < 90]),
                        "C (70-79%)": len([s for s in all_scores if 70 <= s < 80]),
                        "D (60-69%)": len([s for s in all_scores if 60 <= s < 70]),
                        "F (0-59%)": len([s for s in all_scores if s < 60]),
                    }

                    # At-risk students (below 70%)
                    at_risk_students = []
                    improving_students = []

                    for student_id, scores in student_performance.items():
                        if len(scores) >= 2:
                            avg_score = statistics.mean(scores)
                            trend = scores[-1] - scores[0] if len(scores) > 1 else 0

                            if avg_score < 70:
                                at_risk_students.append(student_id)
                            elif (
                                trend > 10
                            ):  # Improving by more than 10 percentage points
                                improving_students.append(student_id)

                    # Find most/least difficult assignments
                    sorted_assignments = sorted(
                        assignment_stats.items(), key=lambda x: x[1]["mean_percentage"]
                    )

                    analytics_data = {
                        "course_overview": course_stats,
                        "grade_distribution": grade_distribution,
                        "assignment_difficulty": {
                            "most_difficult": sorted_assignments[0]
                            if sorted_assignments
                            else None,
                            "least_difficult": sorted_assignments[-1]
                            if sorted_assignments
                            else None,
                        },
                        "student_insights": {
                            "at_risk_count": len(at_risk_students),
                            "improving_count": len(improving_students),
                        },
                        "assignment_statistics": assignment_stats
                        if export_raw
                        else None,
                    }

                    # Format output
                    if output_format == "table":
                        # Create formatted table output
                        output = _format_analytics_table(analytics_data)
                        click.echo(output)
                    else:
                        formatter = FormatterFactory.create_formatter(output_format)
                        output = formatter.format([analytics_data])
                        click.echo(output)
                else:
                    click.echo("No graded submissions found for analysis", err=True)

        except CanvasAPIError as e:
            click.echo(f"Canvas API error: {e}", err=True)
            raise click.ClickException(str(e))
        except ConfigError as e:
            click.echo(f"Configuration error: {e}", err=True)
            raise click.ClickException(str(e))

    asyncio.run(_grade_analytics())


def _format_analytics_table(data: Dict[str, Any]) -> str:
    """Format analytics data as a readable table."""
    output = io.StringIO()

    # Course overview
    course = data["course_overview"]
    output.write(f"Course: {course['course_name']}\n")
    output.write(f"Total Assignments: {course['total_assignments']}\n")
    output.write(f"Total Students: {course['total_students']}\n\n")

    # Grade statistics
    output.write("Grade Statistics:\n")
    output.write(f"  Class Average: {course['class_average']:.1f}%\n")
    output.write(f"  Class Median: {course['class_median']:.1f}%\n")
    output.write(f"  Standard Deviation: {course['std_deviation']:.1f}\n\n")

    # Grade distribution
    output.write("Grade Distribution:\n")
    total_grades = sum(data["grade_distribution"].values())
    for grade_range, count in data["grade_distribution"].items():
        percentage = (count / total_grades * 100) if total_grades > 0 else 0
        output.write(f"  {grade_range}: {count} students ({percentage:.1f}%)\n")
    output.write("\n")

    # Assignment difficulty
    if data["assignment_difficulty"]["most_difficult"]:
        most_diff = data["assignment_difficulty"]["most_difficult"]
        output.write(
            f"Most Difficult Assignment: {most_diff[0]} (avg: {most_diff[1]['mean_percentage']:.1f}%)\n"
        )

    if data["assignment_difficulty"]["least_difficult"]:
        least_diff = data["assignment_difficulty"]["least_difficult"]
        output.write(
            f"Easiest Assignment: {least_diff[0]} (avg: {least_diff[1]['mean_percentage']:.1f}%)\n"
        )
    output.write("\n")

    # Student insights
    insights = data["student_insights"]
    output.write("Student Insights:\n")
    output.write(
        f"  At-Risk Students: {insights['at_risk_count']} (grades below 70%)\n"
    )
    output.write(
        f"  Improving Students: {insights['improving_count']} (showing upward trend)\n"
    )

    return output.getvalue()
