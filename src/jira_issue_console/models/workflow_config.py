"""Workflow configuration model."""

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class WorkflowConfig:
    """Configuration for mapping Jira workflow states.

    This model is a lightweight compatibility wrapper used by some parts of the
    codebase and tests. It exposes a `status_map` for direct status->group mapping
    as well as helper methods expected by core logic.
    """

    status_map: Dict[str, str] = field(default_factory=dict)

    def get_group_for_status(self, status: str) -> str:
        """Return mapped group name for a given status, or the status itself."""
        return self.status_map.get(status, status)

    def get_all_statuses(self) -> Set[str]:
        """Return all statuses known to the mapping."""
        return set(self.status_map.keys())
