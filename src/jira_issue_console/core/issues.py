"""Core business logic for issue handling.

Keep this module pure (no network I/O); use `jira_client` only in higher-level modules or
inject it for tests.
"""
from typing import List, Dict, Any
from .. import jira_client


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
