"""Test CLI cycle time export functionality."""

import os
import tempfile
from typing import List, Dict, Any

import pytest
from pytest_bdd import scenario, given, when, then, parsers

from jira_issue_console.cli import main


@pytest.fixture
def mock_issues(mocker) -> List[Dict[str, Any]]:
    """Return mock issues for testing IssueTimes format."""
    return [
        {
            "key": "TEST-1",
            "id": "1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",
                "resolutiondate": "2025-11-04T16:00:00.000+0000",
                "summary": "First test issue",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "components": [],
                "resolution": {"name": "Fixed"},
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
            "id": "2",
            "fields": {
                "created": "2025-12-24T09:00:00.000+0000",
                "resolutiondate": "2025-12-27T17:00:00.000+0000",
                "summary": "Second test issue",
                "status": {"name": "Done"},
                "issuetype": {"name": "Story"},
                "components": [],
                "resolution": {"name": "Fixed"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-12-25T10:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-12-27T17:00:00.000+0000",
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


@scenario("features/export_cycle_times.feature", "Export cycle times for a project")
def test_export_cycle_times():
    """Test exporting cycle times to CSV."""
    pass


@given(parsers.parse('a project "{project}" with {count:d} issues'))
def project_with_issues(mocker, mock_issues, project: str, count: int):
    """Set up mock issues for the project."""
    assert count == len(mock_issues), (
        f"Test expects {count} issues but mock provides {len(mock_issues)}"
    )

    async def mock_fetch_issues(project_key: str, jql=None):
        assert project_key == project
        return mock_issues

    # Mock jira_client.fetch_issues which is what CLI uses for exports
    mocker.patch(
        "jira_issue_console.jira_client.fetch_issues", side_effect=mock_fetch_issues
    )


@when(
    parsers.parse(
        'I run the CLI with project "{project}" and CSV export to "{csv_path}"'
    )
)
def run_cli_with_csv(project: str, csv_file):
    """Run the CLI with issue times export argument."""
    args = [project, "--issue-times", csv_file]
    main(args)


@then(
    parsers.parse(
        "the CSV file should contain headers and {count:d} rows of cycle time data"
    )
)
def verify_csv_output(csv_file: str, count: int):
    """Verify the CSV output format and content (IssueTimes format)."""
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Verify we have the expected number of data rows
    assert len(lines) == count + 1, (
        f"Expected {count + 1} lines (header + {count} rows), got {len(lines)}"
    )  # +1 for header

    # Verify header contains expected IssueTimes fields
    header = lines[0].strip()
    assert "Project" in header
    assert "Key" in header
    assert "Status" in header
    assert "Created Date" in header

    # Verify we have data rows
    for i in range(1, len(lines)):
        line = lines[i].strip()
        assert len(line) > 0, f"Line {i} is empty"
