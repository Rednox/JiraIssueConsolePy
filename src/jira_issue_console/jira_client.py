"""Async Jira client wrapper (minimal httpx-based implementation).

This isolates HTTP interactions behind a simple async function so core logic stays
independent and easily testable.
"""
from typing import List, Dict, Any, Optional
import httpx
import os
import asyncio
import logging

from .config import from_env, Config

logger = logging.getLogger(__name__)


async def fetch_issues(project_key: str, jql: Optional[str] = None, cfg: Optional[Config] = None) -> List[Dict[str, Any]]:
    """Fetch issues asynchronously from Jira REST API (minimal implementation).

    Returns a list of raw issue dicts. This function is intentionally small — keep
    business logic in `core` and use tests to mock HTTP calls.
    """
    if cfg is None:
        cfg = from_env()

    url = f"{cfg.jira_base_url.rstrip('/')}/rest/api/2/search"
    params = {"jql": jql or f"project={project_key} AND status!=Done"}

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
            async with httpx.AsyncClient(timeout=cfg.request_timeout, headers=headers, auth=auth) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                return data.get("issues", [])
        except httpx.RequestError as exc:
            logger.debug("HTTP request failed on attempt %s: %s", attempt, exc)
            if attempt >= cfg.max_retries:
                logger.warning("Giving up after %s attempts contacting Jira: %s", attempt, exc)
                return []
            # exponential backoff
            backoff = cfg.backoff_factor * (2 ** (attempt - 1))
            await asyncio.sleep(backoff)
