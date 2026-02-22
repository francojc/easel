"""Tests for easel.services.rubrics."""

from unittest.mock import AsyncMock

import httpx
import pytest

from easel.core.client import CanvasClient
from easel.services import CanvasError
from easel.services.rubrics import (
    build_rubric_assessment_form_data,
    get_rubric,
    list_rubrics,
)


@pytest.fixture()
def client():
    return AsyncMock(spec=CanvasClient)


# -- list_rubrics --


async def test_list_rubrics(client):
    client.get_paginated.return_value = [
        {
            "id": 1,
            "title": "Essay Rubric",
            "points_possible": 100,
            "data": [{"id": "_8027"}, {"id": "_8028"}],
        },
    ]

    result = await list_rubrics(client, "1")
    assert len(result) == 1
    assert result[0]["title"] == "Essay Rubric"
    assert result[0]["criteria_count"] == 2


async def test_list_rubrics_empty(client):
    client.get_paginated.return_value = []
    result = await list_rubrics(client, "1")
    assert result == []


async def test_list_rubrics_http_error(client):
    client.get_paginated.side_effect = httpx.HTTPStatusError(
        "error",
        request=httpx.Request("GET", "https://canvas.test/api/v1/courses/1/rubrics"),
        response=httpx.Response(403, text="forbidden"),
    )
    with pytest.raises(CanvasError) as exc_info:
        await list_rubrics(client, "1")
    assert exc_info.value.status_code == 403


# -- get_rubric --


async def test_get_rubric(client):
    client.request.return_value = {
        "id": 1,
        "title": "Essay Rubric",
        "points_possible": 100,
        "data": [
            {
                "id": "_8027",
                "description": "Thesis",
                "points": 25,
                "ratings": [
                    {"id": "r1", "description": "Excellent", "points": 25},
                    {"id": "r2", "description": "Poor", "points": 0},
                ],
            },
        ],
    }

    result = await get_rubric(client, "1", "1")
    assert result["title"] == "Essay Rubric"
    assert len(result["criteria"]) == 1
    assert result["criteria"][0]["id"] == "_8027"
    assert len(result["criteria"][0]["ratings"]) == 2


async def test_get_rubric_http_error(client):
    client.request.side_effect = httpx.HTTPStatusError(
        "error",
        request=httpx.Request("GET", "https://canvas.test/api/v1/courses/1/rubrics/99"),
        response=httpx.Response(404, text="not found"),
    )
    with pytest.raises(CanvasError) as exc_info:
        await get_rubric(client, "1", "99")
    assert exc_info.value.status_code == 404


# -- build_rubric_assessment_form_data --


def test_build_form_data_basic():
    assessment = {
        "_8027": {"points": 25, "comments": "Good thesis"},
        "_8028": {"points": 20},
    }
    pairs = build_rubric_assessment_form_data(assessment)

    keys = [k for k, _ in pairs]
    assert "rubric_assessment[_8027][points]" in keys
    assert "rubric_assessment[_8027][comments]" in keys
    assert "rubric_assessment[_8028][points]" in keys
    # No comments key for _8028
    assert "rubric_assessment[_8028][comments]" not in keys


def test_build_form_data_with_comment():
    assessment = {"_8027": {"points": 10}}
    pairs = build_rubric_assessment_form_data(assessment, comment="Overall good")

    keys = [k for k, _ in pairs]
    assert "comment[text_comment]" in keys
    values = dict(pairs)
    assert values["comment[text_comment]"] == "Overall good"


def test_build_form_data_with_rating_id():
    assessment = {"_8027": {"points": 25, "rating_id": "r1"}}
    pairs = build_rubric_assessment_form_data(assessment)

    keys = [k for k, _ in pairs]
    assert "rubric_assessment[_8027][rating_id]" in keys
