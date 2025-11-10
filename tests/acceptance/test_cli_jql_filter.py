"""Test CLI JQL filtering functionality."""

import pytest
from pytest_bdd import scenario, given, when, then

from jira_issue_console.cli import main


@pytest.fixture
def mock_high_priority_issues(mocker):
    """Return mock high priority issues for testing."""
    return [
        {
            "key": "TEST-1",
            "id": "1",
            "summary": "High priority issue 1",
            "priority": "High",
        },
        {
            "key": "TEST-2",
            "id": "2",
            "summary": "High priority issue 2",
            "priority": "High",
        },
    ]


@scenario("features/jql_filter.feature", "Filter issues by priority")
def test_jql_filter():
    """Test filtering issues by priority using JQL."""
    pass


@given('a project "TEST" with high priority issues')
def project_with_high_priority_issues(mocker, mock_high_priority_issues):
    """Set up mock issues for the project."""

    async def mock_list_issues(project_key: str, jql: str = None):
        assert project_key == "TEST"
        assert "priority = High" in jql
        return mock_high_priority_issues

    mocker.patch(
        "jira_issue_console.core.issues.list_issues", side_effect=mock_list_issues
    )


@when('I run the CLI with project "TEST" and JQL filter "priority = High"')
def run_cli_with_jql(capsys):
    """Run the CLI with JQL filter argument."""
    main(["TEST", "--jql", "priority = High"])


@then("I should only see high priority issues in the output")
def verify_high_priority_output(capsys):
    """Verify that only high priority issues are shown."""
    captured = capsys.readouterr()
    output = captured.out

    # Both TEST-1 and TEST-2 should be in output
    assert "TEST-1" in output
    assert "TEST-2" in output
    assert "High priority issue 1" in output
    assert "High priority issue 2" in output
