from dataclasses import dataclass
from typing import Optional


@dataclass
class Issue:
    id: str
    key: str
    summary: Optional[str] = None
