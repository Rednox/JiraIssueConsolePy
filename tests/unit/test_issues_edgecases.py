import pytest

from jira_issue_console.core import issues


class DummyRaw:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)


@pytest.mark.asyncio
async def test_list_issues_handles_missing_fields(monkeypatch):
    # Arrange: raw issues missing 'fields' or with non-dict fields
    raw = [
        {"id": "1", "key": "PROJ-1", "fields": {"summary": "Has fields"}},
        {"id": "2", "key": "PROJ-2"},
        {"id": "3", "key": "PROJ-3", "fields": "not-a-dict"},
    ]

    async def fake_fetch(project_key, jql=None):
        return raw

    monkeypatch.setattr(
        issues, "jira_client", type("X", (), {"fetch_issues": fake_fetch})
    )

    # Act
    res = await issues.list_issues("PROJ")

    # Assert
    assert isinstance(res, list)
    assert len(res) == 3
    assert res[0]["summary"] == "Has fields"
    assert res[1]["summary"] == ""
    assert res[2]["summary"] == ""
