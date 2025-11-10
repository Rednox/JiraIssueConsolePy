"""Core business logic for issue handling.

Keep this module pure (no network I/O); use `jira_client` only in higher-level modules or
inject it for tests.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from collections import defaultdict
from .. import jira_client
from .workflow_config import WorkflowConfig


def _parse_jira_datetime(s: str) -> datetime:
    """Parse Jira-style timestamps like 2025-10-01T00:00:00.000+0000 into aware datetime."""
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")


async def list_issues(
    project_key: str, jql: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Return a list of simplified issue dicts for the given project.

    Args:
        project_key: The Jira project key (e.g. 'PROJ')
        jql: Optional JQL query to filter issues. If not provided, defaults to
             'project={project_key} AND status!=Done'

    This function delegates to the async `jira_client.fetch_issues` and normalizes
    the minimal shape. Keep business rules here (TDD-driven).
    """
    raw = await jira_client.fetch_issues(project_key, jql=jql)
    result: List[Dict[str, Any]] = []
    for r in raw:
        fields = r.get("fields", {}) if isinstance(r.get("fields"), dict) else {}
        result.append(
            {
                "id": r.get("id"),
                "key": r.get("key"),
                "summary": fields.get("summary", "")
                if fields
                else r.get("summary", ""),
                "priority": fields.get("priority", {}).get("name") if fields else None,
            }
        )
    return result


def normalize_status(status: str, workflow: WorkflowConfig) -> str:
    """Map a Jira status to its workflow group name."""
    return workflow.get_group_for_status(status)


def group_transitions_by_day(
    transitions: List[Dict[str, Any]],
) -> Dict[date, List[Dict[str, Any]]]:
    """Group transitions by day for CFD calculations."""
    daily = defaultdict(list)
    if not transitions:
        return {}
    for t in transitions:
        daily[t["date"].date()].append(t)

    # Return only days that had actual transitions
    return dict(daily)


def extract_transitions_from_issue(
    issue: Dict[str, Any],
    workflow: Optional[WorkflowConfig] = None,
) -> List[Dict[str, Any]]:
    """Extract status transitions from a raw Jira issue.

    Args:
        issue: Raw Jira issue dict with fields and changelog
        workflow: Optional workflow config for status normalization

    Returns:
        List of dicts with 'status' and 'date' (datetime) showing when the issue
        entered each status. The first entry is always the creation status.
    """
    transitions = []

    # Add initial status from creation
    # The initial status is the 'fromString' of the first history item, or a default
    fields = issue.get("fields", {})
    created_str = fields.get("created")
    if not created_str:
        return []

    created_date = _parse_jira_datetime(created_str)

    # Try to get initial status from first changelog entry or current status
    # Changelog can be at top level (Jira API) or in fields (some exports)
    changelog_obj = issue.get("changelog") or fields.get("changelog", {})
    changelog = (
        changelog_obj.get("histories", []) if isinstance(changelog_obj, dict) else []
    )
    initial_status = "Open"  # default
    if changelog:
        first_history = min(changelog, key=lambda h: h["created"])
        for item in first_history.get("items", []):
            if item.get("field") == "status" and item.get("fromString"):
                initial_status = item["fromString"]
                break
    else:
        # If no changelog, use current status
        status_dict = fields.get("status", {})
        if isinstance(status_dict, dict):
            initial_status = status_dict.get("name", "Open")

    # Map through workflow if provided
    if workflow:
        initial_status = normalize_status(initial_status, workflow)

    transitions.append({"status": initial_status, "date": created_date})

    # Add status changes from changelog
    for history in sorted(changelog, key=lambda h: h["created"]):
        for item in history.get("items", []):
            if item.get("field") == "status":
                status = item["toString"]
                if workflow:
                    status = normalize_status(status, workflow)
                transitions.append(
                    {"status": status, "date": _parse_jira_datetime(history["created"])}
                )

    return transitions


def prepare_issues_with_transitions(
    raw_issues: List[Dict[str, Any]],
    workflow: Optional[WorkflowConfig] = None,
) -> List[Dict[str, Any]]:
    """Transform raw Jira issues into format expected by export functions.

    Args:
        raw_issues: List of raw Jira issue dicts
        workflow: Optional workflow config for status normalization

    Returns:
        List of issues with added 'transitions' field
    """
    result = []
    for issue in raw_issues:
        prepared = {
            "key": issue.get("key"),
            "fields": issue.get("fields", {}),
            "transitions": extract_transitions_from_issue(issue, workflow=workflow),
        }
        result.append(prepared)
    return result


async def list_issue_transitions(
    issue_key: str,
    workflow: Optional[WorkflowConfig] = None,
) -> List[Dict[str, Any]]:
    """Return a list of status transitions for an issue, ordered by date.

    Args:
        issue_key: The Jira issue key (e.g. 'PROJ-1')
        workflow: Optional workflow config for status normalization

    Returns:
        List of dicts with 'status' and 'date' (datetime) showing when the issue
        entered each status. The first entry is always the creation status.
    """
    # Fetch issue with changelog
    raw = await jira_client.fetch_issues(
        issue_key.split("-")[0], jql=f"key = {issue_key}"
    )
    if not raw:
        return []

    issue = raw[0]
    return extract_transitions_from_issue(issue, workflow=workflow)
