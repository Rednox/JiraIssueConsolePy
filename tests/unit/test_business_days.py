"""Test business days calculation logic."""
from datetime import datetime, date
from jira_issue_console.core.business_days import compute_business_days

def test_business_days_same_day():
    """Test that same day returns 0 business days."""
    day = date(2025, 11, 4)  # A Tuesday
    assert compute_business_days(day, day) == 0

def test_business_days_weekend():
    """Test that weekends are properly excluded."""
    start = date(2025, 11, 7)  # A Friday
    end = date(2025, 11, 10)   # Next Monday
    # Should only count Friday as 1 business day
    assert compute_business_days(start, end) == 1

def test_business_days_full_week():
    """Test a full work week."""
    start = date(2025, 11, 3)  # A Monday
    end = date(2025, 11, 7)    # Friday same week
    assert compute_business_days(start, end) == 4  # Monday to Friday = 4 days

def test_business_days_with_holidays():
    """Test that holidays are excluded from business days."""
    start = date(2025, 12, 24)  # Wednesday
    end = date(2025, 12, 27)    # Saturday
    # With Dec 25 as holiday, should count 24th and 26th only
    holidays = [date(2025, 12, 25)]  # Christmas
    assert compute_business_days(start, end, holidays) == 2

def test_business_days_datetime():
    """Test that datetime objects work correctly."""
    start = datetime(2025, 11, 4, 9, 0)  # Tuesday 9am
    end = datetime(2025, 11, 6, 17, 0)   # Thursday 5pm
    assert compute_business_days(start, end) == 2