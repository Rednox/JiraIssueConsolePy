"""Simple CLI for JiraIssueConsolePy.

This uses only the standard library so the scaffold can run without extra dependencies.
"""
import argparse
import asyncio
import csv
from typing import Optional, List
import sys

try:
    import click
except Exception:
    click = None

from .core import issues
from .core.csv_export import export_cycle_time_csv
from .core.cycletime import export_cycle_time_rows
from .core.cfd import calculate_cfd_data, export_cfd_rows


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jira-issue-console")
    p.add_argument("project", help="Jira project key to list issues for")
    p.add_argument("--csv", metavar="CSV_FILE", help="Export cycle times to CSV file")
    p.add_argument("--cfd", metavar="CSV_FILE", help="Export CFD (Cumulative Flow Diagram) data to CSV file")
    p.add_argument("--jql", help="Custom JQL query (e.g. 'priority = High AND status = Open')")
    p.add_argument("--input", metavar="JSON_FILE", help="JSON input file (offline mode)")
    p.add_argument("--workflow", metavar="WORKFLOW_FILE", help="Workflow mapping file")
    p.add_argument("--status-timing", metavar="CSV_FILE", help="Export status timing to CSV")
    p.add_argument("--transitions", metavar="CSV_FILE", help="Export transitions to CSV")
    return p


async def async_main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Only pass the jql argument when provided to keep test mocks compatible
    if getattr(args, "jql", None):
        items = await issues.list_issues(args.project, jql=args.jql)
    else:
        items = await issues.list_issues(args.project)

    # Export cycle times if requested
    if args.csv:
        rows = export_cycle_time_rows(items)
        csv_str = export_cycle_time_csv(rows)
        if csv_str is not None:  # type narrowing
            with open(args.csv, "w", encoding="utf-8") as f:
                f.write(csv_str)
            print(f"Exported cycle times to {args.csv}")
        return 0

    # Export CFD data if requested
    if args.cfd:
        cfd_data = calculate_cfd_data(items)
        rows = export_cfd_rows(cfd_data)
        with open(args.cfd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Date"] + sorted(set(status for row in rows for status in row.keys() if status != "Date")))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported CFD data to {args.cfd}")
        return 0

    # Print a simple table header and rows
    header_key = "KEY"
    header_summary = "SUMMARY"
    print(f"{header_key:<16} {header_summary}")
    print(f"{'-'*16} {'-'*40}")
    for it in items:
        key = it.get('key', '')
        summary = it.get('summary', '') or ''
        print(f"{key:<16} {summary}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    try:
        return asyncio.run(async_main(argv))
    except RuntimeError:
        # If an event loop is already running (e.g. pytest-asyncio), delegate
        # execution to a separate thread to avoid "asyncio.run() cannot be
        # called from a running event loop" errors.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(lambda: asyncio.run(async_main(argv)))
            return fut.result()


if click is not None:
    @click.command()
    @click.argument("project")
    @click.option("--csv", "csv_file", help="Export cycle times to CSV file")
    @click.option("--cfd", "cfd_file", help="Export CFD (Cumulative Flow Diagram) data to CSV file")
    @click.option("--jql", "jql", help="Custom JQL query")
    @click.option("--input", "input_file", help="JSON input file (offline mode)")
    @click.option("--workflow", "workflow_file", help="Workflow mapping file")
    @click.option("--status-timing", "status_timing_file", help="Export status timing to CSV")
    @click.option("--transitions", "transitions_file", help="Export transitions to CSV")
    def app(
        project: str,
        csv_file: Optional[str],
        cfd_file: Optional[str],
        jql: Optional[str],
        input_file: Optional[str],
        workflow_file: Optional[str],
        status_timing_file: Optional[str],
        transitions_file: Optional[str]
    ):
        """Compatibility Click command used by tests (runner.invoke(app, args))."""
        argv: List[str] = [project]
        if csv_file:
            argv.extend(["--csv", csv_file])
        if cfd_file:
            argv.extend(["--cfd", cfd_file])
        if jql:
            argv.extend(["--jql", jql])
        if input_file:
            argv.extend(["--input", input_file])
        if workflow_file:
            argv.extend(["--workflow", workflow_file])
        if status_timing_file:
            argv.extend(["--status-timing", status_timing_file])
        if transitions_file:
            argv.extend(["--transitions", transitions_file])
        rc = asyncio.run(async_main(argv))
        if rc:
            raise SystemExit(rc)
        return rc
else:
    # Provide a minimal placeholder so imports don't fail in environments without click
    app = None
