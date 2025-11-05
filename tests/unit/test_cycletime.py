import datetime

from jira_issue_console.core import cycletime


def test_compute_cycle_time_days_resolved():
    # created -> 2025-10-01T00:00:00.000+0000
    # resolved -> 2025-10-04T00:00:00.000+0000
    issue = {
        "id": "1",
        "key": "PROJ-1",
        "fields": {
            "created": "2025-10-01T00:00:00.000+0000",
            "resolutiondate": "2025-10-04T00:00:00.000+0000",
        },
    }
    days = cycletime.compute_cycle_time_days(issue)
    assert days == 3.0


def test_compute_cycle_time_days_unresolved_with_now():
    # created -> 2025-10-01, no resolution -> use provided now
    issue = {
        "id": "2",
        "key": "PROJ-2",
        "fields": {
            "created": "2025-10-01T12:00:00.000+0000",
            # no resolutiondate
        },
    }
    now = datetime.datetime(2025, 10, 3, 12, 0, 0, tzinfo=datetime.timezone.utc)
    days = cycletime.compute_cycle_time_days(issue, now=now)
    assert days == 2.0


def test_export_cycle_times_rows():
    issues = [
        {
            "id": "1",
            "key": "PROJ-1",
            "fields": {"created": "2025-10-01T00:00:00.000+0000", "resolutiondate": "2025-10-04T00:00:00.000+0000"},
        },
        {
            "id": "2",
            "key": "PROJ-2",
            "fields": {"created": "2025-10-01T12:00:00.000+0000"},
        },
    ]
    now = datetime.datetime(2025, 10, 3, 12, 0, 0, tzinfo=datetime.timezone.utc)
    rows = cycletime.export_cycle_time_rows(issues, now=now)
    # Expect rows to contain mapping for each issue
    assert len(rows) == 2
    assert rows[0]["key"] == "PROJ-1"
    assert rows[0]["cycle_time_days"] == 3.0
    assert rows[1]["key"] == "PROJ-2"
    assert rows[1]["cycle_time_days"] == 2.0