"""Tests for CSV export utilities."""

import io
import csv
from typing import Dict, List, Any

from jira_issue_console.core.csv_export import (
    export_rows_csv,
    export_cycle_time_csv,
    export_cfd_csv
)


def test_export_rows_csv_empty():
    """Test exporting empty rows."""
    result = export_rows_csv([])
    assert result == ""


def test_export_rows_csv_basic():
    """Test basic row export functionality."""
    rows = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ]
    result = export_rows_csv(rows)
    
    # Parse back to verify structure
    f = io.StringIO(result)
    reader = csv.DictReader(f)
    read_rows = list(reader)
    
    assert len(read_rows) == 2
    assert read_rows[0] == {"a": "1", "b": "2"}
    assert read_rows[1] == {"a": "3", "b": "4"}


def test_export_cycle_time_csv_basic():
    """Test cycle time CSV export with sample data."""
    rows = [
        {"id": "1", "key": "TEST-1", "created": "2025-11-01T10:00:00.000+0000",
         "resolved": "2025-11-04T16:00:00.000+0000", "cycle_time_days": 2.0},
        {"id": "2", "key": "TEST-2", "created": "2025-12-24T09:00:00.000+0000",
         "resolved": "2025-12-27T17:00:00.000+0000", "cycle_time_days": 1.0},
    ]
    csv_str = export_cycle_time_csv(rows)
    lines = csv_str.strip().splitlines()
    assert lines[0] == "id,key,created,resolved,cycle_time_days"
    assert lines[1].startswith("1,TEST-1,2025-11-01T10:00:00.000+0000,2025-11-04T16:00:00.000+0000,2.0")
    assert lines[2].startswith("2,TEST-2,2025-12-24T09:00:00.000+0000,2025-12-27T17:00:00.000+0000,1.0")


def test_export_cycle_time_csv_empty():
    """Test cycle time CSV export with no data."""
    csv_str = export_cycle_time_csv([])
    assert csv_str == "id,key,created,resolved,cycle_time_days\n"


def test_export_cfd_csv():
    """Test CFD CSV export with dynamic columns."""
    rows = [
        {
            "Date": "2023-01-01",
            "Open": 2,
            "In Progress": 1,
            "Done": 0
        },
        {
            "Date": "2023-01-02",
            "Open": 1,
            "In Progress": 2,
            "Done": 1
        }
    ]
    result = export_cfd_csv(rows)
    
    # Verify structure preserves column order
    f = io.StringIO(result)
    reader = csv.DictReader(f)
    read_rows = list(reader)
    
    assert len(read_rows) == 2
    assert list(read_rows[0].keys()) == ["Date", "Open", "In Progress", "Done"]
    assert read_rows[0]["Date"] == "2023-01-01"
    assert int(read_rows[0]["Open"]) == 2
    assert int(read_rows[1]["Done"]) == 1