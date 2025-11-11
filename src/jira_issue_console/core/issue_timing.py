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
    """Generate CSV-ready rows with status timing data in IssueTimes format.

    Args:
        issues: List of issues with transitions and fields
        workflow: Optional workflow config for status normalization
        use_business_days: If True, only count business days
        holidays: Optional set of holiday dates to exclude

    Returns:
        List of dicts with IssueTimes format (Project, Group, Key, Issuetype, Status,
        Created Date, Component, Category, First Date, Implementation Date, Closed Date,
        status columns in milliseconds, and Resolution)
    """
    rows = []
    holidays = holidays or set()

    for issue in issues:
        # Extract basic fields
        key = issue.get("key", "")
        fields = issue.get("fields", {})
        transitions = issue.get("transitions", [])

        # Extract project from key (e.g., "LIC-247" -> "")
        project = ""  # Empty as in example
        group = ""  # Empty as in example

        # Extract issue type
        issuetype = fields.get("issuetype", {}).get("name", "")

        # Extract current status
        status = fields.get("status", {}).get("name", "")
        if workflow and status:
            status = normalize_status(status, workflow)

        # Extract created date
        created_str = fields.get("created", "")
        if created_str:
            try:
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                created_date = created_dt.strftime("%d.%m.%Y %H:%M:%S")
            except (ValueError, AttributeError):
                created_date = ""
        else:
            created_date = ""

        # Extract components (pipe-separated)
        components = fields.get("components", [])
        component = "|".join([c.get("name", "") for c in components])
        if component:
            component += "|"  # Add trailing pipe as in example

        # Extract resolution
        resolution_obj = fields.get("resolution")
        resolution = resolution_obj.get("name", "") if resolution_obj else ""
        category = resolution  # Category appears to be same as resolution in example

        # Calculate timing in days first
        timing = calculate_status_timing(
            transitions,
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )

        # Convert timing from days to milliseconds
        timing_ms = {status: int(days * 86400000) for status, days in timing.items()}

        # Calculate special dates
        first_date = ""
        implementation_date = ""
        closed_date = ""

        if transitions:
            # First Date: first transition date
            first_trans = transitions[0]
            if first_trans.get("date"):
                first_dt = first_trans["date"]
                if isinstance(first_dt, str):
                    first_dt = datetime.fromisoformat(first_dt.replace("Z", "+00:00"))
                first_date = first_dt.strftime("%d.%m.%Y %H:%M:%S")

            # Implementation Date: first "In Progress" transition
            for trans in transitions:
                trans_status = trans.get("status", "")
                if workflow:
                    trans_status = normalize_status(trans_status, workflow)
                if "progress" in trans_status.lower():
                    trans_dt = trans.get("date")
                    if trans_dt:
                        if isinstance(trans_dt, str):
                            trans_dt = datetime.fromisoformat(
                                trans_dt.replace("Z", "+00:00")
                            )
                        implementation_date = trans_dt.strftime("%d.%m.%Y %H:%M:%S")
                    break

            # Closed Date: last transition if issue is closed/done
            if resolution:  # Has resolution means it's closed
                last_trans = transitions[-1]
                if last_trans.get("date"):
                    last_dt = last_trans["date"]
                    if isinstance(last_dt, str):
                        last_dt = datetime.fromisoformat(last_dt.replace("Z", "+00:00"))
                    closed_date = last_dt.strftime("%d.%m.%Y %H:%M:%S")

        # Build row in IssueTimes format
        row = {
            "Project": project,
            "Group": group,
            "Key": key,
            "Issuetype": issuetype,
            "Status": status,
            "Created Date": created_date,
            "Component": component,
            "Category": category,
            "First Date": first_date,
            "Implementation Date": implementation_date,
            "Closed Date": closed_date,
        }

        # Add status timing columns (in milliseconds)
        row.update(timing_ms)

        # Add Resolution at the end
        row["Resolution"] = resolution

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
