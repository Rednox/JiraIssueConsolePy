"""CSV export utilities for cycle time rows."""
import csv
from typing import List, Dict, Any, Optional, IO
import io


def export_cycle_time_csv(rows: List[Dict[str, Any]], file: Optional[IO[str]] = None) -> str:
    """
    Export cycle time rows to CSV format. If `file` is None, returns CSV as string.
    Columns: id, key, created, resolved, cycle_time_days
    """
    fieldnames = ["id", "key", "created", "resolved", "cycle_time_days"]
    output = file or io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    if file is None:
        return output.getvalue()
    return None
