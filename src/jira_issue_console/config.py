from dataclasses import dataclass, field
from datetime import date, datetime
import os
from typing import Optional, List, Set
import json

from jira_issue_console.core.workflow_config import WorkflowConfig, load_workflow_config


@dataclass
class Config:
    jira_base_url: str
    jira_user: Optional[str]
    jira_api_token: Optional[str]
    request_timeout: float = 10.0
    max_retries: int = 3
    backoff_factor: float = 0.5
    use_business_days: bool = False
    holidays: Set[date] = field(default_factory=set)  # Set of dates to exclude from business day calculations
    workflow_file: Optional[str] = None  # Path to workflow configuration file


def _parse_holidays(holidays_str: Optional[str]) -> Set[date]:
    """Parse holidays from a JSON string of dates (YYYY-MM-DD format)."""
    if not holidays_str:
        return set()
    try:
        dates = json.loads(holidays_str)
        return {date.fromisoformat(d) for d in dates if isinstance(d, str)}
    except (json.JSONDecodeError, ValueError):
        return set()

def from_env() -> Config:
    holidays_json = os.environ.get("JIRA_HOLIDAYS", "[]")  # JSON array of YYYY-MM-DD strings
    
    return Config(
        jira_base_url=os.environ.get("JIRA_BASE_URL", "https://jira.example.com"),
        jira_user=os.environ.get("JIRA_USER"),
        jira_api_token=os.environ.get("JIRA_API_TOKEN"),
        request_timeout=float(os.environ.get("JIRA_REQUEST_TIMEOUT", "10.0")),
        max_retries=int(os.environ.get("JIRA_MAX_RETRIES", "3")),
        backoff_factor=float(os.environ.get("JIRA_BACKOFF_FACTOR", "0.5")),
        use_business_days=bool(os.environ.get("JIRA_USE_BUSINESS_DAYS", "").lower() in ("1", "true", "yes")),
        holidays=_parse_holidays(holidays_json),
        workflow_file=os.environ.get("JIRA_WORKFLOW_FILE"),
    )
