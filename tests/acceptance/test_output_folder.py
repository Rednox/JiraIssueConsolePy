"""Test CLI output folder functionality."""

import os
import tempfile
from typing import List, Dict, Any

import pytest

from jira_issue_console.cli import main


@pytest.fixture
def mock_issues(mocker) -> List[Dict[str, Any]]:
    """Return mock issues in raw Jira format with changelog for testing."""
    return [
        {
            "key": "TEST-1",
            "fields": {
                "created": "2025-11-01T10:00:00.000+0000",
                "status": {"name": "Done"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T14:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-04T16:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "In Progress",
                                "toString": "Done",
                            }
                        ],
                    },
                ]
            },
        },
        {
            "key": "TEST-2",
            "fields": {
                "created": "2025-11-02T09:00:00.000+0000",
                "status": {"name": "Done"},
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2025-11-02T15:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Open",
                                "toString": "In Progress",
                            }
                        ],
                    },
                    {
                        "created": "2025-11-05T11:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "In Progress",
                                "toString": "Done",
                            }
                        ],
                    },
                ]
            },
        },
    ]


@pytest.fixture
def output_dir():
    """Provide a temporary output directory and clean it up after."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_output_folder_generates_all_files(mocker, mock_issues, output_dir):
    """Test that --output generates all three files with correct naming."""

    # Mock jira_client.fetch_issues
    async def mock_fetch_issues(project_key: str, jql=None):
        assert project_key == "TEST"
        return mock_issues

    mocker.patch(
        "jira_issue_console.jira_client.fetch_issues", side_effect=mock_fetch_issues
    )

    # Run CLI with --output parameter
    args = ["TEST", "--output", output_dir]
    main(args)

    # Verify all three files were created
    expected_files = [
        "TEST_CFD.csv",
        "TEST_IssueTimes.csv",
        "TEST_Transitions.csv",
    ]

    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        assert os.path.exists(filepath), f"Expected file {filename} was not created"

    # Verify CFD file has expected structure
    cfd_file = os.path.join(output_dir, "TEST_CFD.csv")
    with open(cfd_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 1  # Should have header + data rows
        assert "Day" in lines[0]

    # Verify IssueTimes (status timing) file has expected structure
    times_file = os.path.join(output_dir, "TEST_IssueTimes.csv")
    with open(times_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 1  # Should have header + data rows
        assert "Key" in lines[0]

    # Verify Transitions file has expected structure
    transitions_file = os.path.join(output_dir, "TEST_Transitions.csv")
    with open(transitions_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 1  # Should have header + data rows
        assert "Key;Transition;Timestamp" in lines[0]


def test_output_folder_with_workflow(mocker, mock_issues, output_dir):
    """Test that --output works with --workflow parameter."""

    # Mock jira_client.fetch_issues
    async def mock_fetch_issues(project_key: str, jql=None):
        return mock_issues

    mocker.patch(
        "jira_issue_console.jira_client.fetch_issues", side_effect=mock_fetch_issues
    )

    # Create a temporary workflow file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as workflow_file:
        workflow_file.write("In Review -> In Progress\n")
        workflow_path = workflow_file.name

    try:
        # Run CLI with --output and --workflow parameters
        args = ["TEST", "--output", output_dir, "--workflow", workflow_path]
        main(args)

        # Verify all files were created
        assert os.path.exists(os.path.join(output_dir, "TEST_CFD.csv"))
        assert os.path.exists(os.path.join(output_dir, "TEST_IssueTimes.csv"))
        assert os.path.exists(os.path.join(output_dir, "TEST_Transitions.csv"))
    finally:
        # Clean up workflow file
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)
