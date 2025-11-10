"""Tests for CFD generation."""

from datetime import date, datetime
from typing import Dict, List

from jira_issue_console.core.cfd import calculate_cfd_data, export_cfd_rows


def _create_test_issue(key: str, transitions: List[Dict[str, str]]) -> Dict:
    """Helper to create test issue data."""
    return {
        "key": key,
        "transitions": [
            {"status": status, "date": datetime.fromisoformat(dt)}
            for status, dt in transitions
        ],
    }


def test_calculate_cfd_data_basic():
    """Test basic CFD calculation with a single issue moving through states."""
    issues = [
        _create_test_issue(
            "TEST-1",
            [
                ("Open", "2023-01-01T10:00:00"),
                ("In Progress", "2023-01-02T14:00:00"),
                ("Done", "2023-01-03T16:00:00"),
            ],
        )
    ]

    cfd = calculate_cfd_data(issues)

    expected = {
        date.fromisoformat("2023-01-01"): {"Open": 1},
        date.fromisoformat("2023-01-02"): {"In Progress": 1},
        date.fromisoformat("2023-01-03"): {"Done": 1},
    }

    assert cfd == expected


def test_calculate_cfd_data_multiple_issues():
    """Test CFD with multiple issues transitioning on same and different days."""
    issues = [
        _create_test_issue(
            "TEST-1",
            [
                ("Open", "2023-01-01T10:00:00"),
                ("In Progress", "2023-01-02T14:00:00"),
                ("Done", "2023-01-03T16:00:00"),
            ],
        ),
        _create_test_issue(
            "TEST-2",
            [
                ("Open", "2023-01-02T09:00:00"),
                ("In Progress", "2023-01-02T15:00:00"),
                ("Done", "2023-01-04T11:00:00"),
            ],
        ),
    ]

    cfd = calculate_cfd_data(issues)

    expected = {
        date.fromisoformat("2023-01-01"): {"Open": 1},
        date.fromisoformat("2023-01-02"): {"In Progress": 2},
        date.fromisoformat("2023-01-03"): {"In Progress": 1, "Done": 1},
        date.fromisoformat("2023-01-04"): {"Done": 2},
    }

    assert cfd == expected


def test_calculate_cfd_with_date_range():
    """Test CFD generation with explicit date range."""
    issues = [
        _create_test_issue(
            "TEST-1",
            [
                ("Open", "2023-01-01T10:00:00"),
                ("In Progress", "2023-01-05T14:00:00"),
                ("Done", "2023-01-10T16:00:00"),
            ],
        )
    ]

    start = date.fromisoformat("2023-01-03")
    end = date.fromisoformat("2023-01-07")

    cfd = calculate_cfd_data(issues, start_date=start, end_date=end)

    # Should only include dates in range, with state from previous transitions
    expected = {
        date.fromisoformat("2023-01-03"): {"Open": 1},
        date.fromisoformat("2023-01-04"): {"Open": 1},
        date.fromisoformat("2023-01-05"): {"In Progress": 1},
        date.fromisoformat("2023-01-06"): {"In Progress": 1},
        date.fromisoformat("2023-01-07"): {"In Progress": 1},
    }

    assert cfd == expected


def test_export_cfd_rows():
    """Test conversion of CFD data to CSV-ready rows."""
    cfd_data = {
        date.fromisoformat("2023-01-01"): {"Open": 2, "In Progress": 1},
        date.fromisoformat("2023-01-02"): {"Open": 1, "In Progress": 2, "Done": 1},
    }

    rows = export_cfd_rows(cfd_data)

    expected = [
        {"Date": "2023-01-01", "Done": 0, "In Progress": 1, "Open": 2},
        {"Date": "2023-01-02", "Done": 1, "In Progress": 2, "Open": 1},
    ]

    assert rows == expected


def test_export_cfd_rows_with_status_list():
    """Test CFD export with explicit status list."""
    cfd_data = {
        date.fromisoformat("2023-01-01"): {"Open": 2, "In Progress": 1},
        date.fromisoformat("2023-01-02"): {"Open": 1, "In Progress": 2},
    }

    # Use different order and subset of statuses
    rows = export_cfd_rows(cfd_data, statuses=["In Progress", "Open"])

    expected = [
        {"Date": "2023-01-01", "In Progress": 1, "Open": 2},
        {"Date": "2023-01-02", "In Progress": 2, "Open": 1},
    ]

    assert rows == expected
