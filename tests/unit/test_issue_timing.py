"""Tests for issue timing calculations."""

from datetime import datetime, date, timezone, timedelta
from typing import Dict, List, Any

import pytest

from jira_issue_console.models.workflow_config import WorkflowConfig
from jira_issue_console.core.issue_timing import (
    calculate_status_timing,
    export_status_timing_rows,
    export_transitions_rows
)


def _dt(s: str) -> datetime:
    """Helper to create timezone-aware datetime."""
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _create_test_issue(key: str, transitions: List[Dict[str, str]]) -> Dict:
    """Helper to create test issue data."""
    return {
        "key": key,
        "transitions": [
            {"status": status, "date": _dt(dt)}
            for status, dt in transitions
        ]
    }


def test_calculate_status_timing_basic():
    """Test basic status timing calculation."""
    transitions = [
        {"status": "Open", "date": _dt("2023-01-01T10:00:00")},
        {"status": "In Progress", "date": _dt("2023-01-02T10:00:00")},
        {"status": "Done", "date": _dt("2023-01-03T10:00:00")}
    ]
    
    timing = calculate_status_timing(transitions)
    
    assert len(timing) == 3
    assert timing["Open"] == pytest.approx(1.0)
    assert timing["In Progress"] == pytest.approx(1.0)
    # "Done" time will depend on current time, but should exist
    assert "Done" in timing


def test_calculate_status_timing_with_workflow():
    """Test timing calculation with workflow status mapping."""
    workflow = WorkflowConfig(status_map={
        "In Review": "In Progress",
        "Testing": "In Progress"
    })
    
    transitions = [
        {"status": "Open", "date": _dt("2023-01-01T10:00:00")},
        {"status": "In Review", "date": _dt("2023-01-02T10:00:00")},
        {"status": "Testing", "date": _dt("2023-01-03T10:00:00")},
        {"status": "Done", "date": _dt("2023-01-04T10:00:00")}
    ]
    
    timing = calculate_status_timing(transitions, workflow=workflow)
    
    assert len(timing) == 3  # Open, In Progress, Done
    assert timing["Open"] == pytest.approx(1.0)
    assert timing["In Progress"] == pytest.approx(2.0)  # Combined In Review + Testing
    assert timing["Done"] > 0  # Time since last transition


def test_calculate_status_timing_business_days():
    """Test timing calculation using business days."""
    # Friday to Tuesday
    transitions = [
        {"status": "Open", "date": _dt("2023-01-06T10:00:00")},  # Friday
        {"status": "In Progress", "date": _dt("2023-01-10T10:00:00")},  # Tuesday
    ]
    
    timing = calculate_status_timing(
        transitions, 
        use_business_days=True
    )
    
    assert timing["Open"] == pytest.approx(3.0)  # Friday + Monday + Tuesday (up to transition time)
    assert "In Progress" in timing


def test_export_status_timing_rows():
    """Test generation of status timing CSV rows."""
    issues = [
        _create_test_issue("TEST-1", [
            ("Open", "2023-01-01T10:00:00"),
            ("In Progress", "2023-01-02T10:00:00"),
            ("Done", "2023-01-03T10:00:00")
        ]),
        _create_test_issue("TEST-2", [
            ("Open", "2023-01-01T10:00:00"),
            ("In Progress", "2023-01-03T10:00:00"),
            ("Done", "2023-01-04T10:00:00")
        ])
    ]
    
    rows = export_status_timing_rows(issues)
    
    assert len(rows) == 2
    assert rows[0]["key"] == "TEST-1"
    assert rows[0]["Open"] == pytest.approx(1.0)
    assert rows[1]["key"] == "TEST-2"
    assert rows[1]["Open"] == pytest.approx(2.0)


def test_export_transitions_rows():
    """Test generation of transition CSV rows."""
    issues = [
        _create_test_issue("TEST-1", [
            ("Open", "2023-01-01T10:00:00"),
            ("In Progress", "2023-01-02T10:00:00"),
            ("Done", "2023-01-03T10:00:00")
        ])
    ]
    
    rows = export_transitions_rows(issues)
    
    assert len(rows) == 2  # Two transitions
    assert rows[0] == {
        "key": "TEST-1",
        "from_status": "Open",
        "to_status": "In Progress",
        "date": "2023-01-02T10:00:00+00:00"
    }
    assert rows[1] == {
        "key": "TEST-1",
        "from_status": "In Progress",
        "to_status": "Done",
        "date": "2023-01-03T10:00:00+00:00"
    }