"""Test JQL query support for Jira issues.

This module tests the custom JQL filtering functionality, ensuring that:
1. JQL queries are properly passed to the Jira API
2. Results are correctly returned and transformed
"""

import pytest
import respx
from jira_issue_console.core import issues


@respx.mock
@pytest.mark.asyncio
async def test_list_issues_with_custom_jql():
    """Test that custom JQL queries are properly passed to the API."""
    # Arrange: mock Jira search endpoint
    url = "https://jira.example.com/rest/api/2/search"
    payload = {
        "issues": [{"id": "1", "key": "PROJ-1", "fields": {"summary": "High priority"}}]
    }
    route = respx.get(url).respond(200, json=payload)

    # Act: call with custom JQL
    custom_jql = "project = PROJ AND priority = High"
    res = await issues.list_issues("PROJ", jql=custom_jql)

    # Assert: check that the JQL was properly passed
    assert route.calls
    assert route.calls[0].request.url.params.get("jql") == custom_jql
    assert len(res) == 1
    assert res[0]["key"] == "PROJ-1"


@respx.mock
@pytest.mark.asyncio
async def test_list_issues_empty_jql():
    """Test that omitting JQL falls back to default project filter."""
    # Arrange: mock Jira search endpoint
    url = "https://jira.example.com/rest/api/2/search"
    payload = {
        "issues": [{"id": "1", "key": "PROJ-1", "fields": {"summary": "Normal issue"}}]
    }
    route = respx.get(url).respond(200, json=payload)

    # Act: call without custom JQL
    res = await issues.list_issues("PROJ")

    # Assert: verify default JQL was used
    assert route.calls
    assert (
        route.calls[0].request.url.params.get("jql") == "project=PROJ AND status!=Done"
    )
    assert len(res) == 1
    assert res[0]["key"] == "PROJ-1"
    assert res[0]["summary"] == "Normal issue"
