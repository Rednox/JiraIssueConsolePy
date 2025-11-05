"""Test CLI cycle time export functionality."""
import os
import tempfile
from datetime import datetime, timezone
from typing import List, Dict, Any

import pytest
from pytest_bdd import scenario, given, when, then, parsers

from jira_issue_console.cli import main


@pytest.fixture
def mock_issues(mocker) -> List[Dict[str, Any]]:
    """Return mock issues for testing."""
    return [
        {
            "key": "TEST-1",
            "id": "1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",
                "resolutiondate": "2025-11-04T16:00:00.000+0000",
                "summary": "First test issue"
            }
        },
        {
            "key": "TEST-2",
            "id": "2",
            "fields": {
                "created": "2025-12-24T09:00:00.000+0000",
                "resolutiondate": "2025-12-27T17:00:00.000+0000",
                "summary": "Second test issue"
            }
        }
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
    assert count == len(mock_issues), f"Test expects {count} issues but mock provides {len(mock_issues)}"
    
    async def mock_list_issues(project_key: str):
        assert project_key == project
        return mock_issues

    mocker.patch("jira_issue_console.core.issues.list_issues", side_effect=mock_list_issues)


@when(parsers.parse('I run the CLI with project "{project}" and CSV export to "{csv_path}"'))
def run_cli_with_csv(project: str, csv_file):
    """Run the CLI with CSV export argument."""
    args = [project, "--csv", csv_file]
    main(args)


@then(parsers.parse("the CSV file should contain headers and {count:d} rows of cycle time data"))
def verify_csv_output(csv_file: str, count: int):
    """Verify the CSV output format and content."""
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Verify header
    assert lines[0].strip() == "id,key,created,resolved,cycle_time_days"
    
    # Verify we have the expected number of data rows
    assert len(lines) == count + 1  # +1 for header
    
    # Verify each line has the expected format (including header)
    for line in lines:
        # Each line should have 5 comma-separated values
        values = line.strip().split(",")
        assert len(values) == 5