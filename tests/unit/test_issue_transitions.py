"""Unit tests for tracking issue transitions through statuses.

These tests ensure we correctly track when issues move between statuses,
which is essential for cycle time calculations.
"""

import pytest
from datetime import datetime, timezone

from jira_issue_console.core import issues


@pytest.mark.asyncio
async def test_list_issue_transitions(respx_mock):
    # Arrange: mock issue with status changes in history
    raw_issue = {
        "id": "1",
        "key": "PROJ-1",
        "fields": {
            "created": "2025-10-01T10:00:00.000+0000",
            "summary": "Test issue",
            "status": {"name": "Done"},
        },
        "changelog": {
            "histories": [
                {
                    "created": "2025-10-01T14:00:00.000+0000",
                    "items": [
                        {
                            "field": "status",
                            "fromString": "To Do",
                            "toString": "In Progress",
                        }
                    ],
                },
                {
                    "created": "2025-10-03T16:00:00.000+0000",
                    "items": [
                        {
                            "field": "status",
                            "fromString": "In Progress",
                            "toString": "Done",
                        }
                    ],
                },
            ]
        },
    }

    # Mock the Jira API response
    respx_mock.get("/rest/api/2/search").mock(
        return_value=respx_mock.Response(200, json={"issues": [raw_issue]})
    )

    # Act: get transitions for the issue
    result = await issues.list_issue_transitions("PROJ-1")

    # Assert: transitions are ordered by date
    assert len(result) == 3  # created + 2 transitions
    assert result[0]["status"] == "To Do"  # initial status
    assert result[0]["date"] == datetime(2025, 10, 1, 10, 0, tzinfo=timezone.utc)

    assert result[1]["status"] == "In Progress"
    assert result[1]["date"] == datetime(2025, 10, 1, 14, 0, tzinfo=timezone.utc)

    assert result[2]["status"] == "Done"
    assert result[2]["date"] == datetime(2025, 10, 3, 16, 0, tzinfo=timezone.utc)
