"""Tests for workflow metrics feature."""

import csv
from pathlib import Path
from pytest_bdd import given, when, then, scenarios, parsers

from jira_issue_console.cli import app


# Import scenarios from feature file
scenarios("features/workflow_metrics.feature")


@given("I have Jira credentials configured")
def configure_jira(monkeypatch):
    """Configure Jira test credentials."""
    monkeypatch.setenv("JIRA_BASE_URL", "https://jira-test")
    monkeypatch.setenv("JIRA_USER", "test")
    monkeypatch.setenv("JIRA_API_TOKEN", "test-token")


@given("a project with issues exists")
def mock_jira_project(respx_mock):
    """Mock Jira API responses."""
    respx_mock.get("/rest/api/2/search").mock(
        return_value=respx_mock.Response(
            200,
            json={
                "issues": [
                    {
                        "key": "TEST-1",
                        "fields": {
                            "created": "2023-01-01T10:00:00.000+0000",
                            "status": {"name": "Open"},
                            "changelog": {
                                "histories": [
                                    {
                                        "created": "2023-01-02T14:00:00.000+0000",
                                        "items": [
                                            {
                                                "field": "status",
                                                "toString": "In Progress",
                                            }
                                        ],
                                    },
                                    {
                                        "created": "2023-01-03T16:00:00.000+0000",
                                        "items": [
                                            {"field": "status", "toString": "Done"}
                                        ],
                                    },
                                ]
                            },
                        },
                    }
                ]
            },
        )
    )


@given("I have a workflow file:", target_fixture="workflow_file")
def create_workflow_file(docstring, tmp_path):
    """Create a workflow mapping file."""
    workflow_file = tmp_path / "workflow.txt"
    workflow_file.write_text(docstring)
    return workflow_file


@when(parsers.parse('I run "{command}"'))
def run_cli(command, runner):
    """Run CLI command."""
    args = command.split()[1:]  # Skip 'jira_issue_console'
    result = runner.invoke(app, args)
    assert result.exit_code == 0


@then(parsers.parse('a CSV file "{filename}" is created'))
def check_csv_exists(filename):
    """Check that CSV file was created."""
    assert Path(filename).exists()


@then(parsers.parse('it has header "{header}"'))
def check_csv_header(header, filename):
    """Check CSV header matches expected."""
    with open(filename) as f:
        reader = csv.reader(f)
        actual_header = next(reader)
        expected_header = header.split(",")
        assert actual_header == expected_header


@then("each row has counts per status")
def check_cfd_rows():
    """Verify CFD CSV structure."""
    with open("cfd.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) > 0
        for row in rows:
            assert "Date" in row
            assert all(v.isdigit() for v in row.values() if v != row["Date"])


@then("each issue has time in each status")
def check_status_timing():
    """Verify status timing CSV structure."""
    with open("status_times.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) > 0
        for row in rows:
            assert "key" in row
            # All non-key columns should be numeric
            for k, v in row.items():
                if k != "key":
                    assert float(v) >= 0


@then("each transition shows status change date")
def check_transitions():
    """Verify transitions CSV structure."""
    with open("transitions.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) > 0
        for row in rows:
            assert all(k in row for k in ["key", "from_status", "to_status", "date"])
            assert "T" in row["date"]  # ISO datetime format


@then(parsers.parse('status "{source}" is mapped to "{target}"'))
def check_status_mapping(source, target):
    """Verify workflow status mapping is applied."""
    with open("transitions.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        found_mapping = False
        for row in rows:
            if row["from_status"] == source:
                assert row["to_status"] == target
                found_mapping = True
            if row["to_status"] == source:
                assert False, f"Found unmapped status: {source}"
        assert found_mapping, f"No transition with status {source} found"
