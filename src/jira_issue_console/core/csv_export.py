"""Functions for exporting data to CSV format."""

import csv
from io import StringIO, TextIOBase
from typing import Any, Dict, List, Optional, Union, TextIO


def export_rows_csv(
    rows: List[Dict[str, Any]], 
    file: Optional[Union[TextIO, TextIOBase]] = None
) -> Optional[str]:
    """Export data rows to CSV format.
    
    Args:
        rows: List of dicts where each dict has same keys (column names)
        file: Optional file-like object to write to. If None, returns string
        
    Returns:
        CSV string if file is None, otherwise None
    """
    if not rows:
        return "" if file is None else None
        
    fieldnames = list(rows[0].keys())
    output: Union[TextIO, TextIOBase, StringIO]
    output = file if file is not None else StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    if file is None:
        if not isinstance(output, StringIO):
            raise TypeError("Expected StringIO when file is None")
        return output.getvalue()
    return None


def export_cycle_time_csv(
    rows: List[Dict[str, Any]], 
    file: Optional[Union[TextIO, TextIOBase]] = None
) -> Optional[str]:
    """Export cycle time rows to CSV format.
    
    Args:
        rows: List of dicts with cycle time data (id, key, created, resolved, cycle_time_days)
        file: Optional file-like object to write to. If None, returns string
        
    Returns:
        CSV string if file is None, otherwise None
    """
    fieldnames = ["id", "key", "created", "resolved", "cycle_time_days"]
    output: Union[TextIO, TextIOBase, StringIO]
    output = file if file is not None else StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    if file is None:
        if not isinstance(output, StringIO):
            raise TypeError("Expected StringIO when file is None")
        return output.getvalue()
    return None


def export_cfd_csv(
    rows: List[Dict[str, Any]], 
    file: Optional[Union[TextIO, TextIOBase]] = None
) -> Optional[str]:
    """Export Cumulative Flow Diagram data rows to CSV format.
    
    Args:
        rows: List of dicts with CFD data (Date column and status columns)
        file: Optional file-like object to write to. If None, returns string
        
    Returns:
        CSV string if file is None, otherwise None
    """
    return export_rows_csv(rows, file)
