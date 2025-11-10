"""Test CLI CFD export functionality."""

import csv
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any

import pytest
from pytest_bdd import scenario, given, when, then, parsers

from jira_issue_console.cli import main


@pytest.fixture
def mock_issues(mocker) -> List[Dict[str, Any]]:
    """Return mock issues in raw Jira format with changelog for testing."""
    return [
        {
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",
                "status": {"name": "Done"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T14:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-04T16:00:00.000+0000",
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
        },
        {
            "key": "TEST-2",
            "fields": {
                "created": "2025-11-02T09:00:00.000+0000",
                "status": {"name": "Done"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T15:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-05T11:00:00.000+0000",
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
        },
    ]


@pytest.fixture
def csv_file():
    """Provide a temporary CSV file and clean it up after."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        yield f.name
    if os.path.exists(f.name):
        os.unlink(f.name)


@scenario("features/export_cfd.feature", "Export CFD data for a project")
def test_export_cfd():
    """Test exporting CFD data to CSV."""
    pass


@given(parsers.parse('a project "{project}" with issues and transitions'))
def project_with_transitions(mocker, mock_issues, project: str):
    """Set up mock issues with transitions for the project."""

    async def mock_fetch_issues(project_key: str, jql=None):
        assert project_key == project
        return mock_issues

    # Mock jira_client.fetch_issues which returns raw Jira issues with changelog
    mocker.patch(
        "jira_issue_console.jira_client.fetch_issues", side_effect=mock_fetch_issues
    )


@when(
    parsers.parse(
        'I run the CLI with project "{project}" and CFD export to "{csv_path}"'
    )
)
def run_cli_with_cfd(project: str, csv_file):
    """Run the CLI with CFD export argument."""
    args = [project, "--cfd", csv_file]
    main(args)


@then("the CFD CSV file should contain status counts per date")
def verify_cfd_output(csv_file: str):
    """Verify the CFD CSV output format and content."""
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Should have data for Nov 1-5
    assert len(rows) == 5

    # Verify expected columns
    assert set(reader.fieldnames) == {"Date", "Open", "In Progress", "Done"}

    # Check a few key points:
    # Nov 1: 1 Open
    assert rows[0]["Date"] == "2025-11-01"
    assert int(rows[0]["Open"]) == 1
    assert int(rows[0]["In Progress"]) == 0
    assert int(rows[0]["Done"]) == 0

    # Nov 2: 2 In Progress (both moved there)
    assert rows[1]["Date"] == "2025-11-02"
    assert int(rows[1]["Open"]) == 0
    assert int(rows[1]["In Progress"]) == 2
    assert int(rows[1]["Done"]) == 0

    # Nov 4: 1 In Progress, 1 Done
    assert rows[3]["Date"] == "2025-11-04"
    assert int(rows[3]["Open"]) == 0
    assert int(rows[3]["In Progress"]) == 1
    assert int(rows[3]["Done"]) == 1

    # Nov 5: 2 Done
    assert rows[4]["Date"] == "2025-11-05"
    assert int(rows[4]["Open"]) == 0
    assert int(rows[4]["In Progress"]) == 0
    assert int(rows[4]["Done"]) == 2
