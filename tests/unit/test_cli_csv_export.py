import pytest

from jira_issue_console import cli


@pytest.mark.asyncio
async def test_cli_writes_csv(tmp_path, monkeypatch):
    # Arrange: mock async issues.list_issues to return two issues
    issues_data = [
        {
            "id": "1",
            "key": "PROJ-1",
            "fields": {
                "created": "2025-10-01T00:00:00.000+0000",
                "resolutiondate": "2025-10-04T00:00:00.000+0000",
            },
        },
        {
            "id": "2",
            "key": "PROJ-2",
            "fields": {"created": "2025-10-01T12:00:00.000+0000"},
        },
    ]

    async def fake_list(project_key, jql=None):
        return issues_data

    # monkeypatch the imported module in cli
    monkeypatch.setattr(cli.issues, "list_issues", fake_list)

    out_file = tmp_path / "out.csv"

    # Act: run the CLI (it's synchronous entrypoint calling asyncio.run)
    rc = cli.main(["PROJ", "--csv", str(out_file)])
    assert rc == 0

    # Assert: file exists and contents look like CSV with header and two lines
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert text[0].strip() == "id,key,created,resolved,cycle_time_days"
    # must contain the two keys
    joined = "\n".join(text)
    assert "PROJ-1" in joined
    assert "PROJ-2" in joined
