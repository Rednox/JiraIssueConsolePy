"""Workflow configuration and status mapping support.

This module handles parsing and managing Jira workflow configurations, including
status groups and special state markers for cycle time calculations.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, TextIO, Union


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

    Supports two formats:

    Simple mapping format:
        Status1 -> TargetGroup
        Status2 -> TargetGroup

    Full format with groups:
        GroupName:Status1:Status2:Status3
        Group2:Status4
        <First>InitialGroup
        <Last>FinalGroup
        <Implementation>ImplementationGroup

    Returns:
        WorkflowConfig instance
    """
    if isinstance(file, str):
        with open(file, "r", encoding="utf-8") as f:
            return parse_workflow_file(f)

    status_groups: Dict[str, List[str]] = {}
    initial_state = None
    final_state = None
    implementation_state = None
    simple_mappings: Dict[str, str] = {}
    has_markers = False

    for line in file:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("<"):
            # Parse special markers (full format)
            has_markers = True
            if line.startswith("<First>"):
                initial_state = line[len("<First>") :].strip()
            elif line.startswith("<Last>"):
                final_state = line[len("<Last>") :].strip()
            elif line.startswith("<Implementation>"):
                implementation_state = line[len("<Implementation>") :].strip()
        elif "->" in line:
            # Simple mapping format: "From -> To"
            parts = line.split("->", 1)
            if len(parts) == 2:
                from_status = parts[0].strip()
                to_group = parts[1].strip()
                simple_mappings[from_status] = to_group
        else:
            # Parse status group definition (full format)
            parts = [p.strip() for p in line.split(":")]
            group_name = parts[0]
            statuses = [s for s in parts[1:] if s]  # Filter out empty strings
            # Always add the group name itself as a status if no other statuses
            if not statuses:
                statuses = [group_name]
            status_groups[group_name] = statuses

    # If we have simple mappings but no full format, create status_groups from mappings
    if simple_mappings and not has_markers:
        # Build status groups from simple mappings
        reverse_map: Dict[str, List[str]] = {}
        for from_status, to_group in simple_mappings.items():
            if to_group not in reverse_map:
                reverse_map[to_group] = []
            reverse_map[to_group].append(from_status)

        # Convert to status_groups format
        for group_name, statuses in reverse_map.items():
            if group_name in status_groups:
                status_groups[group_name].extend(statuses)
            else:
                status_groups[group_name] = statuses

        # Use simple defaults for markers
        all_groups = sorted(status_groups.keys())
        initial_state = all_groups[0] if all_groups else "Open"
        final_state = all_groups[-1] if all_groups else "Done"
        implementation_state = (
            all_groups[len(all_groups) // 2] if all_groups else "In Progress"
        )

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
