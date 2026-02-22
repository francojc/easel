"""Rubrics service — list, detail, and assessment form-data builder."""

from __future__ import annotations

from typing import Any

import httpx

from easel.core.client import CanvasClient
from easel.services import CanvasError


async def list_rubrics(
    client: CanvasClient,
    course_id: str,
) -> list[dict[str, Any]]:
    """Fetch all rubrics for a course."""
    try:
        rubrics = await client.get_paginated(
            f"/courses/{course_id}/rubrics",
        )
    except httpx.HTTPStatusError as exc:
        raise CanvasError(
            f"Failed to list rubrics for course {course_id}: {exc.response.text}",
            status_code=exc.response.status_code,
        ) from exc

    return [
        {
            "id": r["id"],
            "title": r.get("title", ""),
            "points_possible": r.get("points_possible", ""),
            "criteria_count": len(r.get("data", [])),
        }
        for r in rubrics
    ]


async def get_rubric(
    client: CanvasClient,
    course_id: str,
    rubric_id: str,
) -> dict[str, Any]:
    """Fetch a single rubric with full criteria detail."""
    try:
        r = await client.request(
            "get",
            f"/courses/{course_id}/rubrics/{rubric_id}",
            params={"include[]": ["assessments"]},
        )
    except httpx.HTTPStatusError as exc:
        raise CanvasError(
            f"Failed to get rubric {rubric_id}: {exc.response.text}",
            status_code=exc.response.status_code,
        ) from exc

    criteria = []
    for c in r.get("data", []):
        criteria.append(
            {
                "id": c.get("id", ""),
                "description": c.get("description", ""),
                "points": c.get("points", 0),
                "ratings": [
                    {
                        "id": rt.get("id", ""),
                        "description": rt.get("description", ""),
                        "points": rt.get("points", 0),
                    }
                    for rt in c.get("ratings", [])
                ],
            }
        )

    return {
        "id": r["id"],
        "title": r.get("title", ""),
        "points_possible": r.get("points_possible", ""),
        "criteria": criteria,
    }


def build_rubric_assessment_form_data(
    rubric_assessment: dict[str, dict[str, Any]],
    comment: str | None = None,
) -> list[tuple[str, str]]:
    """Build bracket-notation form data for rubric grade submission.

    Canvas expects form-encoded keys like::

        rubric_assessment[_8027][points]=5
        rubric_assessment[_8027][comments]=Good work

    Args:
        rubric_assessment: Mapping of criterion_id to dict with
            ``points`` and optional ``comments``.
        comment: Overall submission comment.

    Returns:
        List of (key, value) tuples suitable for ``form_data``.
    """
    pairs: list[tuple[str, str]] = []

    for criterion_id, assessment in rubric_assessment.items():
        prefix = f"rubric_assessment[{criterion_id}]"
        pairs.append((f"{prefix}[points]", str(assessment["points"])))
        if "comments" in assessment:
            pairs.append((f"{prefix}[comments]", str(assessment["comments"])))
        if "rating_id" in assessment:
            pairs.append((f"{prefix}[rating_id]", str(assessment["rating_id"])))

    if comment is not None:
        pairs.append(("comment[text_comment]", comment))

    return pairs
