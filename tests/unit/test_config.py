"""Test configuration handling."""
from datetime import date
import os
from jira_issue_console.config import from_env, Config


def test_config_defaults():
    """Test default configuration values."""
    os.environ.clear()
    config = from_env()
    assert config.jira_base_url == "https://jira.example.com"
    assert config.jira_user is None
    assert config.jira_api_token is None
    assert config.request_timeout == 10.0
    assert config.max_retries == 3
    assert config.backoff_factor == 0.5
    assert config.use_business_days is False
    assert config.holidays == set()


def test_config_holidays():
    """Test holiday configuration parsing."""
    os.environ["JIRA_HOLIDAYS"] = '["2025-12-25", "2025-12-26"]'
    config = from_env()
    assert config.holidays == {date(2025, 12, 25), date(2025, 12, 26)}


def test_config_use_business_days():
    """Test business days flag configuration."""
    test_cases = [
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("", False),
        ("0", False),
        ("no", False),
    ]
    
    for value, expected in test_cases:
        os.environ["JIRA_USE_BUSINESS_DAYS"] = value
        config = from_env()
        assert config.use_business_days == expected, f"Failed for value: {value}"


def test_invalid_holidays():
    """Test handling of invalid holiday configurations."""
    test_cases = [
        "invalid json",
        '["not-a-date"]',
        '{"not": "an-array"}',
        "[42]",
    ]
    
    for value in test_cases:
        os.environ["JIRA_HOLIDAYS"] = value
        config = from_env()
        assert config.holidays == set(), f"Failed for value: {value}"