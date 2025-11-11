"""Tests for offline JSON input feature."""

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from jira_issue_console.cli import app


# Import scenarios from feature file
scenarios("features/offline_input.feature")


@pytest.fixture
def example_json(tmp_path):
    """Copy example.json to temporary directory."""
    src = Path(__file__).parent / ".." / "fixtures" / "example.json"
    dst = tmp_path / "example.json"
    shutil.copy(src, dst)
    return dst


@given("I have a Jira JSON export file")
def json_file(example_json):
    """Provide example.json fixture."""
    return example_json


@given("I have a workflow file:", target_fixture="workflow_file")
def workflow_file(docstring, tmp_path):
    """Create workflow mapping file."""
    workflow_path = tmp_path / "workflow.txt"
    workflow_path.write_text(docstring)
    return workflow_path


@when(parsers.parse('I run "{command}"'))
def run_cli(command, runner, monkeypatch, tmp_path):
    """Run CLI command with JSON input."""
    monkeypatch.chdir(tmp_path)  # Run in temp dir
    args = command.split()[1:]  # Skip 'jira_issue_console'
    result = runner.invoke(app, args)
    if result.exit_code != 0:
        print(f"CLI output: {result.output}")
        print(f"Exception: {result.exception}")
    assert result.exit_code == 0


@then(parsers.parse('a CSV file "{filename}" is created'))
def check_csv_created(filename, tmp_path):
    """Check that CSV file was created."""
    assert (tmp_path / filename).exists()


@then("it contains cycle times for the exported issues")
def check_cycle_times(tmp_path):
    """Verify cycle time CSV content."""
    with open(tmp_path / "cycle_times.csv") as f:
        content = f.read()
        # Should have header and TEST-1 data
        assert "id,key,created,resolved,cycle_time_days" in content
        assert "TEST-1" in content


@then("it shows daily status counts")
def check_cfd_content(tmp_path):
    """Verify CFD CSV content."""
    with open(tmp_path / "cfd.csv") as f:
        content = f.read()
        assert "Day" in content
        assert "Open" in content
        assert "In Progress" in content
        assert "Done" in content


@then("status transitions use mapped names")
def check_mapped_transitions(tmp_path):
    """Verify workflow mapping in transitions."""
    with open(tmp_path / "transitions.csv") as f:
        content = f.read()
        assert "In Progress" in content  # mapped status
        assert "In Review" not in content  # original status
