"""Core business logic for issue handling.

Keep this module pure (no network I/O); use `jira_client` only in higher-level modules or
inject it for tests.
"""
from typing import List, Dict, Any
from datetime import datetime
from .. import jira_client


def _parse_jira_datetime(s: str) -> datetime:
    """Parse Jira-style timestamps like 2025-10-01T00:00:00.000+0000 into aware datetime."""
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")


async def list_issues(project_key: str, jql: str = None) -> List[Dict[str, Any]]:
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
        result.append({
            "id": r.get("id"),
            "key": r.get("key"),
            "summary": fields.get("summary", "") if fields else r.get("summary", ""),
            "priority": fields.get("priority", {}).get("name") if fields else None,
        })
    return result


async def list_issue_transitions(issue_key: str) -> List[Dict[str, Any]]:
    """Return a list of status transitions for an issue, ordered by date.
    
    Args:
        issue_key: The Jira issue key (e.g. 'PROJ-1')
    
    Returns:
        List of dicts with 'status' and 'date' (datetime) showing when the issue
        entered each status. The first entry is always the creation status.
    """
    # Fetch issue with changelog
    raw = await jira_client.fetch_issues(issue_key.split("-")[0], 
                                       jql=f"key = {issue_key}")
    if not raw:
        return []
    
    issue = raw[0]
    transitions = []
    
    # Add initial status from creation
    created_date = _parse_jira_datetime(issue["fields"]["created"])
    initial_status = "To Do"  # assuming default initial status
    transitions.append({
        "status": initial_status,
        "date": created_date
    })
    
    # Add status changes from changelog
    changelog = issue.get("changelog", {}).get("histories", [])
    for history in changelog:
        for item in history.get("items", []):
            if item.get("field") == "status":
                transitions.append({
                    "status": item["toString"],
                    "date": _parse_jira_datetime(history["created"])
                })
    
    return transitions
