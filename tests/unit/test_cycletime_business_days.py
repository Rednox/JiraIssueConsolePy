"""Test business days cycle time calculations."""
import pytest
from datetime import date
from jira_issue_console.core.cycletime import compute_cycle_time_days, export_cycle_time_rows
from jira_issue_console.config import Config


def test_compute_cycle_time_business_days():
    """Test cycle time calculation using business days."""
    # Create a resolved issue spanning a weekend
    issue = {
        "fields": {
            "created": "2025-11-01T10:00:00.000+0000",  # Saturday
            "resolutiondate": "2025-11-04T16:00:00.000+0000"  # Tuesday
        }
    }
    
    # Without business days, should be ~3.25 days
    assert compute_cycle_time_days(issue) == pytest.approx(3.25, rel=0.01)
    
    # With business days, should be 2 days (Monday + Tuesday)
    config = Config(
        jira_base_url="https://example.com",
        jira_user=None,
        jira_api_token=None,
        use_business_days=True,
        holidays=set()
    )
    assert compute_cycle_time_days(issue, config=config) == 2.0


def test_compute_cycle_time_with_holidays():
    """Test cycle time calculation with holidays."""
    # Create an issue spanning holidays
    issue = {
        "fields": {
            "created": "2025-12-24T09:00:00.000+0000",  # Wednesday
            "resolutiondate": "2025-12-27T17:00:00.000+0000"  # Saturday
        }
    }
    
    # Set Christmas and Boxing Day as holidays
    config = Config(
        jira_base_url="https://example.com",
        jira_user=None,
        jira_api_token=None,
        use_business_days=True,
        holidays={date(2025, 12, 25), date(2025, 12, 26)}
    )
    
    # Should only count Wednesday as 1 business day
    assert compute_cycle_time_days(issue, config=config) == 1.0


def test_export_cycle_time_rows_business_days():
    """Test exporting cycle times using business days."""
    issues = [
        {
            "id": "1",
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",  # Saturday
                "resolutiondate": "2025-11-04T16:00:00.000+0000"  # Tuesday
            }
        },
        {
            "id": "2",
            "key": "TEST-2",
            "fields": {
                "created": "2025-12-24T09:00:00.000+0000",  # Wednesday
                "resolutiondate": "2025-12-27T17:00:00.000+0000"  # Saturday
            }
        }
    ]
    
    # Configure with holidays
    config = Config(
        jira_base_url="https://example.com",
        jira_user=None,
        jira_api_token=None,
        use_business_days=True,
        holidays={date(2025, 12, 25), date(2025, 12, 26)}  # Christmas holidays
    )
    
    rows = export_cycle_time_rows(issues, config=config)
    assert len(rows) == 2
    assert rows[0]["cycle_time_days"] == 2.0  # TEST-1: Monday + Tuesday
    assert rows[1]["cycle_time_days"] == 1.0  # TEST-2: Only Wednesday counts