"""Calculate timing statistics for issue statuses and transitions."""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Set

from .workflow_config import WorkflowConfig
from .business_days import compute_business_days
from .issues import normalize_status


def calculate_status_timing(
    transitions: List[Dict[str, Any]],
    workflow: Optional[WorkflowConfig] = None,
    use_business_days: bool = False,
    holidays: Optional[Set[date]] = None,
) -> Dict[str, float]:
    """Calculate time spent in each status.

    Args:
        transitions: List of status transitions with dates
        workflow: Optional workflow config for status normalization
        use_business_days: If True, only count business days
        holidays: Optional set of holiday dates to exclude

    Returns:
        Dict mapping status names to days spent in that status
    """
    if not transitions:
        return {}

    timing: Dict[str, float] = {}
    holidays = holidays or set()

    # Process transitions in chronological order
    for i in range(len(transitions) - 1):
        current = transitions[i]
        next_trans = transitions[i + 1]

        status = current["status"]
        if workflow:
            status = normalize_status(status, workflow)

        start = current["date"]
        end = next_trans["date"]

        if use_business_days:
            days = float(compute_business_days(start, end, holidays))
            if (
                end.date() > start.date()
                and end.date().weekday() < 5
                and end.date() not in holidays
            ):
                days += 1.0
        else:
            days = (end - start).total_seconds() / 86400.0

        timing[status] = timing.get(status, 0.0) + days

    # Add time in final status up to now if not resolved
    final = transitions[-1]
    status = final["status"]
    if workflow:
        status = normalize_status(status, workflow)

    now = datetime.now(final["date"].tzinfo)
    if use_business_days:
        days = float(compute_business_days(final["date"], now, holidays))
        if (
            now.date() > final["date"].date()
            and now.date().weekday() < 5
            and now.date() not in holidays
        ):
            days += 1.0
    else:
        days = (now - final["date"]).total_seconds() / 86400.0

    timing[status] = timing.get(status, 0.0) + days

    return timing


def export_status_timing_rows(
    issues: List[Dict[str, Any]],
    workflow: Optional[WorkflowConfig] = None,
    use_business_days: bool = False,
    holidays: Optional[Set[date]] = None,
) -> List[Dict[str, Any]]:
    """Generate CSV-ready rows with status timing data.

    Args:
        issues: List of issues with transitions
        workflow: Optional workflow config for status normalization
        use_business_days: If True, only count business days
        holidays: Optional set of holiday dates to exclude

    Returns:
        List of dicts with issue key and time spent in each status
    """
    rows = []
    holidays = holidays or set()

    for issue in issues:
        timing = calculate_status_timing(
            issue["transitions"],
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )

        row = {"key": issue["key"]}
        row.update(timing)
        rows.append(row)

    return rows


def export_transitions_rows(
    issues: List[Dict[str, Any]], workflow: Optional[WorkflowConfig] = None
) -> List[Dict[str, Any]]:
    """Generate CSV-ready rows with all status transitions.

    Args:
        issues: List of issues with transitions
        workflow: Optional workflow config for status normalization

    Returns:
        List of dicts with Key, Transition (status), and Timestamp
    """
    rows = []

    for issue in issues:
        transitions = issue["transitions"]

        # Add rows for each transition (including the first one as Created)
        for trans in transitions:
            status = trans["status"]

            if workflow:
                status = normalize_status(status, workflow)

            # Format timestamp as DD.MM.YYYY HH:MM:SS
            timestamp = trans["date"]
            formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")

            rows.append(
                {
                    "Key": issue["key"],
                    "Transition": status,
                    "Timestamp": formatted_timestamp,
                }
            )

    return rows
