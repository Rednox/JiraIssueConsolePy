"""Test config loading including workflow configuration."""
import os
import tempfile
from datetime import date
import pytest

from jira_issue_console.config import Config, from_env


def test_load_workflow_config_from_env(monkeypatch, tmp_path):
    """Test loading workflow configuration from environment."""
    # Create temp workflow file
    workflow_path = tmp_path / "workflow.txt"
    workflow_path.write_text("""
Funnel:Open
Analysis
Backlog
Done:Closed
<First>Analysis
<Last>Done
<Implementation>Backlog
""".strip())

    # Set up environment
    monkeypatch.setenv("JIRA_BASE_URL", "https://jira.test.com")
    monkeypatch.setenv("JIRA_USER", "testuser")
    monkeypatch.setenv("JIRA_API_TOKEN", "testtoken")
    monkeypatch.setenv("JIRA_WORKFLOW_FILE", str(workflow_path))

    # Load config
    config = from_env()
    assert config.workflow_file == str(workflow_path)

def test_config_without_workflow():
    """Test that config works without workflow file."""
    config = Config(
        jira_base_url="https://jira.test.com",
        jira_user="user",
        jira_api_token="token",
        workflow_file=None,
    )
    assert config.workflow_file is None