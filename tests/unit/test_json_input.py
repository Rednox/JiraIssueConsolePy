"""Tests for JSON file input support with security checks."""

import json
import os
import stat
import tempfile
from pathlib import Path
import pytest

from jira_issue_console.core.json_input import load_issues_from_json


@pytest.fixture
def example_json(tmp_path):
    """Create a temporary example.json file."""
    data = {
        "issues": [
            {
                "id": "10001",
                "key": "TEST-1",
                "fields": {
                    "summary": "Test issue",
                    "status": {"name": "Open"}
                }
            }
        ]
    }
    json_file = tmp_path / "example.json"
    json_file.write_text(json.dumps(data))
    # Secure permissions
    json_file.chmod(0o600)
    return str(json_file)


def test_load_nonexistent_file():
    """Test loading a nonexistent file."""
    with pytest.raises(FileNotFoundError):
        load_issues_from_json("nonexistent.json")


def test_load_directory(tmp_path):
    """Test loading a directory instead of file."""
    with pytest.raises(ValueError, match="not a regular file"):
        load_issues_from_json(str(tmp_path))


def test_malformed_json(tmp_path):
    """Test loading malformed JSON."""
    json_file = tmp_path / "malformed.json"
    json_file.write_text("{bad json")
    json_file.chmod(0o600)
    
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_issues_from_json(str(json_file))


def test_load_issues_from_json(example_json):
    """Test loading issues from JSON file."""
    issues = load_issues_from_json(example_json)
    assert len(issues) == 1
    assert issues[0]["key"] == "TEST-1"
    assert issues[0]["fields"]["status"]["name"] == "Open"


def test_load_issues_from_json_single_issue(tmp_path):
    """Test loading single issue JSON."""
    data = {
        "id": "10001",
        "key": "TEST-1",
        "fields": {"status": {"name": "Open"}}
    }
    json_file = tmp_path / "single.json"
    json_file.write_text(json.dumps(data))
    json_file.chmod(0o600)
    
    issues = load_issues_from_json(str(json_file))
    assert len(issues) == 1
    assert issues[0]["key"] == "TEST-1"


def test_load_issues_from_json_list(tmp_path):
    """Test loading JSON list of issues."""
    data = [
        {
            "id": "10001",
            "key": "TEST-1",
            "fields": {"status": {"name": "Open"}}
        },
        {
            "id": "10002",
            "key": "TEST-2",
            "fields": {"status": {"name": "Done"}}
        }
    ]
    json_file = tmp_path / "list.json"
    json_file.write_text(json.dumps(data))
    json_file.chmod(0o600)
    
    issues = load_issues_from_json(str(json_file))
    assert len(issues) == 2
    assert issues[0]["key"] == "TEST-1"
    assert issues[1]["key"] == "TEST-2"


def test_load_issues_from_json_invalid(tmp_path):
    """Test loading invalid JSON format."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text('"not an object or array"')
    json_file.chmod(0o600)
    
    with pytest.raises(ValueError, match="Invalid JSON format"):
        load_issues_from_json(str(json_file))


def test_load_issues_from_json_missing_fields(tmp_path):
    """Test loading issue with missing required fields."""
    data = {"key": "TEST-1"}  # Missing fields
    json_file = tmp_path / "missing_fields.json"
    json_file.write_text(json.dumps(data))
    json_file.chmod(0o600)
    
    with pytest.raises(ValueError, match="missing required fields"):
        load_issues_from_json(str(json_file))


def test_load_issues_from_json_invalid_type(tmp_path):
    """Test loading issue with invalid field types."""
    data = {
        "key": "TEST-1",
        "fields": "not a dict"  # Invalid type
    }
    json_file = tmp_path / "invalid_type.json"
    json_file.write_text(json.dumps(data))
    json_file.chmod(0o600)
    
    with pytest.raises(ValueError, match="fields must be a dict"):
        load_issues_from_json(str(json_file))


def test_file_permissions_warning(tmp_path, caplog):
    """Test file permission warnings."""
    json_file = tmp_path / "loose_perms.json"
    data = {
        "key": "TEST-1",
        "fields": {"status": {"name": "Open"}}
    }
    json_file.write_text(json.dumps(data))
    
    # Set loose permissions (readable by others)
    json_file.chmod(0o644)
    
    # Should work but log warning
    with caplog.at_level("WARNING"):
        issues = load_issues_from_json(str(json_file))
        assert len(issues) == 1
        assert "loose permissions" in caplog.text