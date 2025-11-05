"""Cycle time calculations and exports.

Functions are pure and accept optional `now` and `config` parameters to keep tests deterministic.
"""
from typing import Dict, List, Any, Optional, Set
import datetime

from jira_issue_console.config import Config
from jira_issue_console.core.business_days import compute_business_days


def _parse_jira_datetime(s: str) -> datetime.datetime:
    """Parse Jira-style timestamps like 2025-10-01T00:00:00.000+0000 into aware datetime."""
    # Example format: %Y-%m-%dT%H:%M:%S.%f%z
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")


def compute_cycle_time_days(
    issue: Dict[str, Any],
    now: Optional[datetime.datetime] = None,
    config: Optional[Config] = None
) -> float:
    """Compute cycle time in days between `created` and `resolutiondate`.

    If `resolutiondate` is missing, `now` is used (or current UTC time when `now` is None).
    If `config` is provided and `config.use_business_days` is True, only business days are counted.
    Returns a float number of days (may be fractional for calendar days, or integer for business days).
    """
    fields = issue.get("fields", {})
    created_s = fields.get("created")
    if not created_s:
        raise ValueError("issue has no created field")

    created = _parse_jira_datetime(created_s)

    res_s = fields.get("resolutiondate")
    if res_s:
        resolved = _parse_jira_datetime(res_s)
    else:
        if now is None:
            now = datetime.datetime.now(datetime.timezone.utc)
        resolved = now

    if config and config.use_business_days:
        # compute_business_days counts business days from start (inclusive)
        # up to end (exclusive). For cycle time semantics we want to count
        # the resolved day as a business day when the resolution occurs on a
        # business day and the interval spans at least one day.
        base = compute_business_days(created, resolved, config.holidays or set())
        # include resolved date if it's a business day and interval spans days
        try:
            resolved_date = resolved.date()
            created_date = created.date()
        except Exception:
            resolved_date = resolved
            created_date = created

        if created_date < resolved_date:
            if resolved_date.weekday() < 5 and resolved_date not in (config.holidays or set()):
                base += 1

        return float(base)
    else:
        delta = resolved - created
        return delta.total_seconds() / 86400.0


def export_cycle_time_rows(
    issues: List[Dict[str, Any]],
    now: Optional[datetime.datetime] = None,
    config: Optional[Config] = None
) -> List[Dict[str, Any]]:
    """Return exportable rows containing key, created, resolved and cycle_time_days."""
    rows: List[Dict[str, Any]] = []
    for issue in issues:
        fields = issue.get("fields", {})
        created = fields.get("created")
        resolved = fields.get("resolutiondate")
        ct = compute_cycle_time_days(issue, now=now, config=config)
        rows.append({
            "id": issue.get("id"),
            "key": issue.get("key"),
            "created": created,
            "resolved": resolved,
            "cycle_time_days": ct,
        })
    return rows
