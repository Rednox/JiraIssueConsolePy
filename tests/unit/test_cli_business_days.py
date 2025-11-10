"""Test CLI with --business-days flag."""

import pytest

from jira_issue_console import cli, jira_client


def test_cli_business_days_flag(tmp_path, monkeypatch):
    """Test that --business-days flag uses business days for calculations."""
    # Arrange: mock issues spanning a weekend
    # Friday to Tuesday should be 3 calendar days but only 2 business days
    issues_data = [
        {
            "id": "1",
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",  # Saturday
                "resolutiondate": "2025-11-04T16:00:00.000+0000",  # Tuesday
            },
        },
    ]

    async def fake_fetch(project_key, jql=None):
        return issues_data

    monkeypatch.setattr(jira_client, "fetch_issues", fake_fetch)

    out_file = tmp_path / "business_days.csv"

    # Act: run CLI with --business-days flag
    rc = cli.main(["TEST", "--csv", str(out_file), "--business-days"])
    assert rc == 0

    # Assert: file exists and cycle time is in business days (2 days, not 3.25)
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip()

    # Should contain 2.0 for business days (Monday + Tuesday)
    assert "2.0" in text or "2," in text
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
                "resolutiondate": "2025-11-04T16:00:00.000+0000",  # Tuesday (6 hours later)
            },
        },
    ]

    async def fake_fetch(project_key, jql=None):
        return issues_data

    monkeypatch.setattr(jira_client, "fetch_issues", fake_fetch)

    out_file = tmp_path / "calendar_days.csv"

    # Act: run CLI WITHOUT --business-days flag
    rc = cli.main(["TEST", "--csv", str(out_file)])
    assert rc == 0

    # Assert: file exists and cycle time is in calendar days (~3.25 days)
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8").strip()

    # Should contain approximately 3.25 days (Saturday 10am to Tuesday 4pm)
    assert "3.2" in text or "3.3" in text  # Allow some tolerance
    assert "TEST-1" in text
