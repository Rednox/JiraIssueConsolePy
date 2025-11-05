"""Shared pytest fixtures for all tests."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a Click CLI test runner for acceptance tests."""
    return CliRunner()
