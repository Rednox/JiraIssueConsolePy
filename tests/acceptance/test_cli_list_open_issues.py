import respx
import pytest
from jira_issue_console import cli


@respx.mock
def test_cli_prints_table(capfd):
    # Arrange: mock Jira search endpoint
    url = "https://jira.example.com/rest/api/2/search"
    payload = {"issues": [{"id": "1", "key": "PROJ-1", "fields": {"summary": "First issue"}}]}
    respx.get(url).respond(200, json=payload)

    # Act: run CLI with a project argument
    cli.main(["PROJ"])  # prints to stdout

    # Capture stdout
    captured = capfd.readouterr()
    out = captured.out.strip()

    # Assert: expect a header and the issue line
    assert "KEY" in out and "SUMMARY" in out
    assert "PROJ-1" in out
