"""HTTP client and offline input handling for Jira data."""

import asyncio
import logging
from typing import Dict, List, Optional, Any

import httpx

from .config import Config, from_env
from .core.json_input import load_issues_from_json

logger = logging.getLogger(__name__)


async def fetch_issues(
    project_key: str,
    jql: Optional[str] = None,
    cfg: Optional[Config] = None,
    input_file: Optional[str] = None,
    expand_changelog: bool = True,
) -> List[Dict[str, Any]]:
    """Fetch issues from Jira REST API or load from JSON file.

    Args:
        project_key: The Jira project key (e.g., 'PROJ')
        jql: Optional JQL query to filter issues
        cfg: Optional configuration override
        input_file: Optional path to JSON file containing issue data
        expand_changelog: If True, request changelog data from API (default: True)

    Returns:
        List of raw issue dicts either from API or JSON file

    If input_file is provided, data will be loaded from file instead of API.
    """
    if input_file:
        return load_issues_from_json(input_file)

    if cfg is None:
        cfg = from_env()

    url = f"{cfg.jira_base_url.rstrip('/')}/rest/api/2/search"
    params: Dict[str, Any] = {"jql": jql or f"project={project_key} AND status!=Done"}
    if expand_changelog:
        params["expand"] = "changelog"

    # Determine auth headers/auth object from config
    jira_user = cfg.jira_user
    jira_token = cfg.jira_api_token

    headers = {}
    auth = None
    if jira_token:
        if jira_token.strip().lower().startswith("bearer ") and not jira_user:
            headers["Authorization"] = jira_token.strip()
        elif jira_user:
            auth = httpx.BasicAuth(jira_user, jira_token)
        else:
            headers["Authorization"] = jira_token.strip()

    attempt = 0
    while True:
        attempt += 1
        try:
            async with httpx.AsyncClient(
                timeout=cfg.request_timeout, headers=headers, auth=auth
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data: Dict[str, Any] = resp.json()
                issues: List[Dict[str, Any]] = data.get("issues", [])
                return issues
        except httpx.RequestError as exc:
            logger.debug("HTTP request failed on attempt %s: %s", attempt, exc)
            if attempt >= cfg.max_retries:
                logger.warning(
                    "Giving up after %s attempts contacting Jira: %s", attempt, exc
                )
                return []
            # exponential backoff
            backoff = cfg.backoff_factor * (2 ** (attempt - 1))
            await asyncio.sleep(backoff)
