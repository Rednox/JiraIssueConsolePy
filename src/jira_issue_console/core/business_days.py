"""Business days calculation utilities."""

from datetime import datetime, date
from typing import Union, Optional, List


def compute_business_days(
    start_date: Union[datetime, date],
    end_date: Union[datetime, date],
    holidays: Optional[Union[List[date], set[date]]] = None,
) -> int:
    """
    Calculate the number of business days between two dates, excluding weekends and holidays.

    Args:
        start_date: The start date/datetime
        end_date: The end date/datetime
        holidays: Optional list of holiday dates to exclude

    Returns:
        int: Number of business days between start and end dates (inclusive)
    """
    # Convert to date if datetime
    start = start_date.date() if isinstance(start_date, datetime) else start_date
    end = end_date.date() if isinstance(end_date, datetime) else end_date

    # If start is after end, zero
    if start >= end:
        # The function counts business days from start (inclusive) up to end (exclusive).
        # This means start == end -> 0 days.
        return 0

    holidays = holidays or []
    holiday_set = set(holidays)

    # Initialize counter
    business_days = 0
    current = start

    # Iterate from start (inclusive) up to end (exclusive)
    while current < end:
        # Check if it's a business day (not weekend and not holiday)
        if current.weekday() < 5 and current not in holiday_set:
            business_days += 1
        current = date.fromordinal(current.toordinal() + 1)

    return business_days
