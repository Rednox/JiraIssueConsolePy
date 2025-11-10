"""Test issue status mapping and transition tracking."""

import pytest
from datetime import datetime, timezone

from jira_issue_console.core.workflow_config import WorkflowConfig
from jira_issue_console.core.issues import (
    list_issue_transitions,
    normalize_status,
    group_transitions_by_day,
)


def create_workflow_config() -> WorkflowConfig:
    """Create test workflow config."""
    return WorkflowConfig(
        status_groups={
            "Funnel": ["Open", "Reopened"],
            "Analysis": ["Analysis"],
            "Backlog": ["Backlog"],
            "In Progress": ["In Development", "In Dev"],
            "Released": ["E2E Test", "In Review"],
            "Done": ["Closed", "Resolved"],
        },
        initial_state="Analysis",
        final_state="Done",
        implementation_state="In Progress",
    )


@pytest.fixture
def workflow_config():
    """Provide test workflow configuration."""
    return create_workflow_config()


@pytest.fixture
def mock_issue():
    """Create a mock issue with transitions."""
    return {
        "id": "1",
        "key": "TEST-1",
        "fields": {
            "created": "2025-11-01T10:00:00.000+0000",
            "summary": "Test issue",
            "status": {"name": "In Development"},
            "resolutiondate": "2025-11-04T16:00:00.000+0000",
        },
        "changelog": {
            "histories": [
                {
                    "created": "2025-11-01T12:00:00.000+0000",
                    "items": [
                        {
                            "field": "status",
                            "fromString": "Open",
                            "toString": "Analysis",
                        }
                    ],
                },
                {
                    "created": "2025-11-02T10:00:00.000+0000",
                    "items": [
                        {
                            "field": "status",
                            "fromString": "Analysis",
                            "toString": "In Development",
                        }
                    ],
                },
                {
                    "created": "2025-11-04T16:00:00.000+0000",
                    "items": [
                        {
                            "field": "status",
                            "fromString": "In Development",
                            "toString": "Closed",
                        }
                    ],
                },
            ]
        },
    }


@pytest.mark.skip(
    reason="Async test setup incomplete - needs pytest-asyncio configuration"
)
@pytest.mark.asyncio
async def test_list_issue_transitions_with_workflow():
    """Test that transitions are properly mapped to workflow groups."""
    transitions = await list_issue_transitions("TEST-1", workflow_config)

    assert transitions[0]["status"] == "Funnel"  # Initial status mapped to group
    assert transitions[1]["status"] == "Analysis"
    assert transitions[2]["status"] == "In Progress"  # "In Development" mapped to group
    assert transitions[3]["status"] == "Done"  # "Closed" mapped to group


def test_normalize_status(workflow_config):
    """Test status normalization through workflow groups."""
    assert normalize_status("Open", workflow_config) == "Funnel"
    assert normalize_status("In Development", workflow_config) == "In Progress"
    assert (
        normalize_status("Unknown", workflow_config) == "Unknown"
    )  # Unmapped stays as-is


def test_group_transitions_by_day(mock_issue, workflow_config):
    """Test grouping transitions into daily buckets."""
    transitions = [
        {"status": "Funnel", "date": datetime(2025, 11, 1, 10, 0, tzinfo=timezone.utc)},
        {
            "status": "Analysis",
            "date": datetime(2025, 11, 1, 12, 0, tzinfo=timezone.utc),
        },
        {
            "status": "In Progress",
            "date": datetime(2025, 11, 2, 10, 0, tzinfo=timezone.utc),
        },
        {"status": "Done", "date": datetime(2025, 11, 4, 16, 0, tzinfo=timezone.utc)},
    ]

    daily = group_transitions_by_day(transitions)
    assert len(daily) == 3  # Nov 1, 2, 4 (only days with actual transitions)

    # Check Nov 1 transitions
    nov1 = daily[datetime(2025, 11, 1).date()]
    assert len(nov1) == 2
    assert nov1[0]["status"] == "Funnel"
    assert nov1[1]["status"] == "Analysis"
