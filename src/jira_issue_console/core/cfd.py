"""Cumulative Flow Diagram (CFD) generation and calculations."""

from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set

from .workflow_config import WorkflowConfig
from .issues import normalize_status


def calculate_cfd_data(
    issues: List[Dict[str, Any]],
    workflow: Optional[WorkflowConfig] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[date, Dict[str, int]]:
    """Calculate daily issue counts per status for a CFD.

    Args:
        issues: List of issues with their transitions
        workflow: Optional workflow config for status mapping
        start_date: Optional start date to include (inclusive)
        end_date: Optional end date to include (inclusive)

    Returns:
        Dict mapping dates to counters of issues in each status
    """
    # Track each issue's status over time
    issue_states: Dict[str, List[tuple[date, str]]] = {}

    # Process each issue's transitions
    for issue in issues:
        issue_key = issue["key"]
        transitions = issue["transitions"]

        # Sort transitions by date
        sorted_transitions = sorted(transitions, key=lambda t: t["date"])

        # Build list of (date, status) tuples
        states = []
        for trans in sorted_transitions:
            status = trans["status"]
            if workflow:
                status = normalize_status(status, workflow)
            trans_date = (
                trans["date"].date()
                if isinstance(trans["date"], datetime)
                else trans["date"]
            )
            states.append((trans_date, status))

        if states:
            issue_states[issue_key] = states

    # Determine the date range
    if not issue_states:
        return {}

    all_transition_dates = [d for states in issue_states.values() for d, _ in states]
    first_date = start_date if start_date else min(all_transition_dates)
    last_date = end_date if end_date else max(all_transition_dates)

    # Build CFD by simulating each day
    result: Dict[date, Dict[str, int]] = {}
    current_date = first_date

    while current_date <= last_date:
        counts: Counter[str] = Counter()

        # For each issue, find its status on this date
        for issue_key, states in issue_states.items():
            # Find the most recent transition on or before current_date
            issue_status = None
            for trans_date, status in states:
                if trans_date <= current_date:
                    issue_status = status
                else:
                    break

            # Count the issue if it had entered a status by this date
            if issue_status:
                counts[issue_status] += 1

        # Store snapshot (only non-zero counts)
        if counts:
            result[current_date] = dict(counts)
        else:
            result[current_date] = {}

        current_date = date.fromordinal(current_date.toordinal() + 1)

    return result


def export_cfd_rows(
    cfd_data: Dict[date, Dict[str, int]], statuses: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Convert CFD data into rows for CSV export.

    Args:
        cfd_data: CFD data as returned by calculate_cfd_data()
        statuses: Optional list of status names to include (and their order)
                 If not provided, will use all statuses found in data

    Returns:
        List of dicts with 'Day' (DD.MM.YYYY format) and status columns
    """
    if not cfd_data:
        return []

    # Get all status names if not provided
    if not statuses:
        status_set: Set[str] = set()
        for counts in cfd_data.values():
            status_set.update(counts.keys())
        statuses = sorted(status_set)

    # Convert to rows
    rows = []
    for day in sorted(cfd_data.keys()):
        # Format date as DD.MM.YYYY
        row: Dict[str, Any] = {"Day": day.strftime("%d.%m.%Y")}
        counts = cfd_data[day]
        for status in statuses:
            # keep numeric counts (ints) for CSV consumers/tests
            row[status] = counts.get(status, 0)
        rows.append(row)

    return rows
