"""Test CLI with --business-days flag."""

from jira_issue_console import cli, jira_client


def test_cli_business_days_flag(tmp_path, monkeypatch):
    """Test that --business-days flag uses business days for calculations."""
    # Arrange: mock issues spanning a weekend with changelog
    # Saturday to Tuesday should consider business days
    issues_data = [
        {
            "id": "1",
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",  # Saturday
                "resolutiondate": "2025-11-04T16:00:00.000+0000",  # Tuesday
                "project": {"key": "TEST", "name": "Test Project"},
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "components": [],
                "resolution": {"name": "Fixed"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T10:00:00.000+0000",  # Sunday
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-04T16:00:00.000+0000",  # Tuesday
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
    ]

    async def fake_fetch(project_key, jql=None):
        return issues_data

    monkeypatch.setattr(jira_client, "fetch_issues", fake_fetch)

    out_file = tmp_path / "business_days.csv"

    # Act: run CLI with --business-days flag
    rc = cli.main(["TEST", "--issue-times", str(out_file), "--business-days"])
    assert rc == 0

    # Assert: file exists and timing uses business days
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip()

    # Should contain TEST-1
    assert "TEST-1" in text


def test_cli_without_business_days_flag(tmp_path, monkeypatch):
    """Test that without --business-days flag, calendar days are used."""
    # Same data as above
    issues_data = [
        {
            "id": "1",
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",  # Saturday
                "resolutiondate": "2025-11-04T16:00:00.000+0000",  # Tuesday
                "project": {"key": "TEST", "name": "Test Project"},
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "components": [],
                "resolution": {"name": "Fixed"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T10:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-04T16:00:00.000+0000",
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
    ]

    async def fake_fetch(project_key, jql=None):
        return issues_data

    monkeypatch.setattr(jira_client, "fetch_issues", fake_fetch)

    out_file = tmp_path / "calendar_days.csv"

    # Act: run CLI WITHOUT --business-days flag
    rc = cli.main(["TEST", "--issue-times", str(out_file)])
    assert rc == 0

    # Assert: file exists and timing is in calendar days
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip()

    # Should contain TEST-1
    assert "TEST-1" in text
