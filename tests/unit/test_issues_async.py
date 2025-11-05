import pytest
import respx
import httpx
import asyncio

from jira_issue_console.core import issues


@respx.mock
@pytest.mark.asyncio
async def test_list_issues_respx():
    # Arrange: mock Jira search endpoint
    url = "https://jira.example.com/rest/api/2/search"
    payload = {"issues": [{"id": "1", "key": "PROJ-1", "fields": {"summary": "First issue"}}]}
    respx.get(url).respond(200, json=payload)

    # Act
    res = await issues.list_issues("PROJ")

    # Assert
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["key"] == "PROJ-1"
    assert res[0]["summary"] == "First issue"
