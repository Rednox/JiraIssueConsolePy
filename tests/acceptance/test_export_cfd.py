"""Test CLI CFD export functionality."""

import csv
import os
import tempfile
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

    # Should have data for the last 5 years (approximately 1825 days)
    # The actual count will vary based on test run date
    assert len(rows) > 1000, (
        f"Expected at least 1000 rows for 5 years of data, got {len(rows)}"
    )

    # Verify expected columns
    assert set(reader.fieldnames) == {"Day", "Open", "In Progress", "Done"}

    # Find the rows for our test dates (Nov 1-5, 2025)
    rows_by_date = {row["Day"]: row for row in rows}

    # Check a few key points:
    # Nov 1: 1 Open
    assert "01.11.2025" in rows_by_date
    assert int(rows_by_date["01.11.2025"]["Open"]) == 1
    assert int(rows_by_date["01.11.2025"]["In Progress"]) == 0
    assert int(rows_by_date["01.11.2025"]["Done"]) == 0

    # Nov 2: 2 In Progress (both moved there)
    assert "02.11.2025" in rows_by_date
    assert int(rows_by_date["02.11.2025"]["Open"]) == 0
    assert int(rows_by_date["02.11.2025"]["In Progress"]) == 2
    assert int(rows_by_date["02.11.2025"]["Done"]) == 0

    # Nov 4: 1 In Progress, 1 Done
    assert "04.11.2025" in rows_by_date
    assert int(rows_by_date["04.11.2025"]["Open"]) == 0
    assert int(rows_by_date["04.11.2025"]["In Progress"]) == 1
    assert int(rows_by_date["04.11.2025"]["Done"]) == 1

    # Nov 5: 2 Done
    assert "05.11.2025" in rows_by_date
    assert int(rows_by_date["05.11.2025"]["Open"]) == 0
    assert int(rows_by_date["05.11.2025"]["In Progress"]) == 0
    assert int(rows_by_date["05.11.2025"]["Done"]) == 2
