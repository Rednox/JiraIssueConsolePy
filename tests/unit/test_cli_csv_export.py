from jira_issue_console import cli, jira_client


def test_cli_writes_csv(tmp_path, monkeypatch):
    # Arrange: mock jira_client.fetch_issues to return two issues with changelog
    issues_data = [
        {
            "id": "1",
            "key": "PROJ-1",
            "fields": {
                "created": "2025-10-01T00:00:00.000+0000",
                "resolutiondate": "2025-10-04T00:00:00.000+0000",
                "project": {"key": "PROJ", "name": "Project"},
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "components": [],
                "resolution": {"name": "Fixed"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-10-02T00:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-10-04T00:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "In Progress",
                                "toString": "Done",
                            }
                        ],
                    },
                ]
            },
        },
        {
            "id": "2",
            "key": "PROJ-2",
            "fields": {
                "created": "2025-10-01T12:00:00.000+0000",
                "project": {"key": "PROJ", "name": "Project"},
                "status": {"name": "Open"},
                "issuetype": {"name": "Story"},
                "components": [],
                "resolution": None,
            },
            "changelog": {"histories": []},
        },
    ]

    async def fake_fetch(project_key, jql=None):
        return issues_data

    # Mock jira_client.fetch_issues which is what CLI uses for issue times export
    monkeypatch.setattr(jira_client, "fetch_issues", fake_fetch)

    out_file = tmp_path / "out.csv"

    # Act: run the CLI (it's synchronous entrypoint calling asyncio.run)
    rc = cli.main(["PROJ", "--issue-times", str(out_file)])
    assert rc == 0

    # Assert: file exists and contents look like CSV with IssueTimes format
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip()
    # Check for IssueTimes format headers
    assert "Key" in text
    assert "Project" in text
    assert "Status" in text
    # must contain the two keys
    assert "PROJ-1" in text
    assert "PROJ-2" in text
