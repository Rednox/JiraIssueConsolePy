"""Workflow configuration and status mapping support.

This module handles parsing and managing Jira workflow configurations, including
status groups and special state markers for cycle time calculations.
"""
from dataclasses import dataclass
from typing import Dict, List, Set, TextIO, Union
import os


@dataclass
class WorkflowConfig:
    """Workflow configuration including status groups and special states."""
    # Map from group name (e.g. "In Progress") to list of Jira statuses
    status_groups: Dict[str, List[str]]
    # Special state markers
    initial_state: str
    final_state: str
    implementation_state: str

    def get_group_for_status(self, status: str) -> str:
        """Return the group name for a given Jira status."""
        for group, statuses in self.status_groups.items():
            if status in statuses:
                return group
        return status  # If no group mapping found, return as-is

    def get_all_statuses(self) -> Set[str]:
        """Return set of all known status names."""
        result = set()
        for statuses in self.status_groups.values():
            result.update(statuses)
        return result


def parse_workflow_file(file: Union[str, TextIO]) -> WorkflowConfig:
    """Parse a workflow configuration file.

    Args:
        file: Either a file path or file-like object containing workflow config

    Format:
        GroupName:Status1:Status2:Status3
        Group2:Status4
        <First>InitialGroup
        <Last>FinalGroup
        <Implementation>ImplementationGroup

    Returns:
        WorkflowConfig instance
    """
    if isinstance(file, str):
        with open(file, 'r', encoding='utf-8') as f:
            return parse_workflow_file(f)

    status_groups: Dict[str, List[str]] = {}
    initial_state = None
    final_state = None
    implementation_state = None

    for line in file:
        line = line.strip()
        if not line:
            continue

        if line.startswith('<'):
            # Parse special markers
            if line.startswith('<First>'):
                initial_state = line[len('<First>'):].strip()
            elif line.startswith('<Last>'):
                final_state = line[len('<Last>'):].strip()
            elif line.startswith('<Implementation>'):
                implementation_state = line[len('<Implementation>'):].strip()
        else:
            # Parse status group definition
            parts = [p.strip() for p in line.split(':')]
            group_name = parts[0]
            statuses = [s for s in parts[1:] if s]  # Filter out empty strings
            # Always add the group name itself as a status if no other statuses
            if not statuses:
                statuses = [group_name]
            status_groups[group_name] = statuses

    # Validate configuration
    if not initial_state:
        raise ValueError("Missing <First> marker in workflow config")
    if not final_state:
        raise ValueError("Missing <Last> marker in workflow config")
    if not implementation_state:
        raise ValueError("Missing <Implementation> marker in workflow config")

    # Validate state references
    all_groups = set(status_groups.keys())
    for state in (initial_state, final_state, implementation_state):
        if state not in all_groups:
            raise ValueError(f"State marker '{state}' references undefined state group")

    return WorkflowConfig(
        status_groups=status_groups,
        initial_state=initial_state,
        final_state=final_state,
        implementation_state=implementation_state,
    )


def load_workflow_config(path: str) -> WorkflowConfig:
    """Load workflow configuration from a file path."""
    return parse_workflow_file(path)