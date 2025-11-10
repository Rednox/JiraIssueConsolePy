import os
import base64
import respx
import pytest

from jira_issue_console import jira_client


@respx.mock
@pytest.mark.asyncio
async def test_fetch_issues_sets_basic_auth():
    # Arrange: set environment for basic auth
    os.environ["JIRA_BASE_URL"] = "https://jira.example.com"
    os.environ["JIRA_USER"] = "user@example.com"
    os.environ["JIRA_API_TOKEN"] = "myapitoken"

    url = "https://jira.example.com/rest/api/2/search"
    payload = {"issues": []}
    route = respx.get(url).respond(200, json=payload)

    # Act
    _res = await jira_client.fetch_issues("PROJ")

    # Assert: request was made and Authorization header exists and is Basic
    assert route.calls, "No HTTP call was recorded"
    req = route.calls[0].request
    auth_header = req.headers.get("authorization")
    assert auth_header is not None
    assert auth_header.startswith("Basic ")

    # verify base64 payload
    expected = base64.b64encode(b"user@example.com:myapitoken").decode()
    assert auth_header.split()[1] == expected


@respx.mock
@pytest.mark.asyncio
async def test_fetch_issues_sets_bearer_auth():
    # Arrange: set environment for bearer auth token (token includes Bearer prefix)
    os.environ["JIRA_BASE_URL"] = "https://jira.example.com"
    # Remove JIRA_USER to force bearer flow
    os.environ.pop("JIRA_USER", None)
    os.environ["JIRA_API_TOKEN"] = "Bearer sometoken123"

    url = "https://jira.example.com/rest/api/2/search"
    payload = {"issues": []}
    route = respx.get(url).respond(200, json=payload)

    # Act
    _res = await jira_client.fetch_issues("PROJ")

    # Assert
    assert route.calls, "No HTTP call was recorded"
    req = route.calls[0].request
    auth_header = req.headers.get("authorization")
    assert auth_header is not None
    assert auth_header == "Bearer sometoken123"
