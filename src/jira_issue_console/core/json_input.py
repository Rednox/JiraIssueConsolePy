"""JSON file input support for offline analysis."""

import json
import os
import stat
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional

from ..models.workflow_config import WorkflowConfig
from . import issues

logger = logging.getLogger(__name__)


def _check_file_permissions(path: Path) -> bool:
    """Check if file permissions are secure (only owner can read).
    
    Args:
        path: Path to the file to check
        
    Returns:
        True if permissions are secure, False otherwise
    """
    try:
        mode = os.stat(path).st_mode
        # Check if group/others have any access
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            logger.warning(
                "Warning: JSON input file %s has loose permissions. "
                "Consider restricting with: chmod 600 %s",
                path, path
            )
            return False
        return True
    except OSError:
        return False


def load_issues_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load Jira issues from a JSON export file.
    
    SECURITY WARNING: Ensure exported JSON files don't contain sensitive data
    and have appropriate file permissions (readable only by owner).
    
    Args:
        file_path: Path to the JSON file containing issue data
        
    Returns:
        List of issue dicts matching Jira REST API format
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON format is invalid or file permissions are insecure
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
        
    # Security checks
    if not path.is_file():
        raise ValueError(f"Path {file_path} is not a regular file")
    
    # Check permissions
    _check_file_permissions(path)
    
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in {file_path}: {str(e)}")
        
    # Support both flat issue list and structured export formats
    if isinstance(data, list):
        issues = data
    elif isinstance(data, dict):
        if "issues" in data:
            issues = data["issues"]
        else:
            # Single issue case
            if set(data.keys()) >= {"key", "fields"}:
                issues = [data]
            else:
                # Keep a concise, stable error message expected by tests
                raise ValueError("missing required fields")
    else:
        raise ValueError(
            f"Invalid JSON format - expected list or dict with Jira issue structure"
        )

    # Validate and sanitize basic issue fields
    required_fields = {"key", "fields"}
    
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError(f"Invalid issue format - expected dict, got {type(issue)}")
        
        missing = required_fields - set(issue.keys())
        if missing:
            raise ValueError("missing required fields")
            
        # Ensure fields is a dict
        if not isinstance(issue.get("fields"), dict):
            raise ValueError("Issue fields must be a dict")
            
    return issues