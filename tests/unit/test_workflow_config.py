"""Test workflow configuration parsing and management."""
import textwrap
from io import StringIO
from datetime import date

import pytest

from jira_issue_console.core.workflow_config import (
    WorkflowConfig,
    load_workflow_config,
    parse_workflow_file
)


def test_parse_workflow_file_basic():
    """Test basic workflow file parsing."""
    content = textwrap.dedent("""
        Funnel:Open:Reopened
        Analysis
        Backlog
        In Progress:In Development:In Dev
        Released:E2E Test:In Review
        Done:Closed:Resolved
        <First>Analysis
        <Last>Done
        <Implementation>In Progress
    """).strip()

    config = parse_workflow_file(StringIO(content))
    assert isinstance(config, WorkflowConfig)
    assert config.status_groups["Funnel"] == ["Open", "Reopened"]
    assert config.status_groups["Analysis"] == ["Analysis"]
    assert config.status_groups["In Progress"] == ["In Development", "In Dev"]
    assert config.initial_state == "Analysis"
    assert config.final_state == "Done"
    assert config.implementation_state == "In Progress"


def test_parse_workflow_file_with_whitespace():
    """Test that whitespace is properly handled."""
    content = textwrap.dedent("""
        Funnel:Inbound Channel:  Open  :Reopened
        In Progress:In Implementation:  In Dev  :
        Done:Closed
        <First>Funnel
        <Last>Done
        <Implementation>In Progress
    """).strip()

    config = parse_workflow_file(StringIO(content))
    assert config.status_groups["Funnel"] == ["Inbound Channel", "Open", "Reopened"]
    assert config.status_groups["In Progress"] == ["In Implementation", "In Dev"]
    assert config.status_groups["Done"] == ["Closed"]


def test_load_workflow_config(tmp_path):
    """Test loading workflow config from a file."""
    workflow_file = tmp_path / "workflow.txt"
    workflow_file.write_text(textwrap.dedent("""
        Funnel:Open
        In Progress
        Done:Closed
        <First>Funnel
        <Last>Done
        <Implementation>In Progress
    """).strip())

    config = load_workflow_config(str(workflow_file))
    assert config.status_groups["Funnel"] == ["Open"]
    assert config.initial_state == "Funnel"
    assert config.final_state == "Done"


def test_missing_required_markers():
    """Test that missing required markers raise ValueError."""
    content = textwrap.dedent("""
        Funnel:Open
        Done:Closed
        <First>Funnel
    """).strip()

    with pytest.raises(ValueError, match="Missing <Last> marker"):
        parse_workflow_file(StringIO(content))

def test_invalid_state_reference():
    """Test that referencing undefined states raises ValueError."""
    content = textwrap.dedent("""
        Funnel:Open
        Done:Closed
        <First>Unknown
        <Last>Done
        <Implementation>In Progress
    """).strip()

    with pytest.raises(ValueError, match="references undefined state"):
        parse_workflow_file(StringIO(content))