"""Simple CLI for JiraIssueConsolePy.

This uses only the standard library so the scaffold can run without extra dependencies.
"""
import argparse
import asyncio
from .core import issues
from .core.csv_export import export_cycle_time_csv
from .core.cycletime import export_cycle_time_rows


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jira-issue-console")
    p.add_argument("project", help="Jira project key to list issues for")
    p.add_argument("--csv", metavar="CSV_FILE", help="Export cycle times to CSV file")
    p.add_argument("--jql", help="Custom JQL query (e.g. 'priority = High AND status = Open')")
    return p


async def async_main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Only pass the jql argument when provided to keep test mocks compatible
    if getattr(args, "jql", None):
        items = await issues.list_issues(args.project, jql=args.jql)
    else:
        items = await issues.list_issues(args.project)
    # If CSV requested, export cycle times
    if args.csv:
        rows = export_cycle_time_rows(items)
        csv_str = export_cycle_time_csv(rows)
        with open(args.csv, "w", encoding="utf-8") as f:
            f.write(csv_str)
        print(f"Exported cycle times to {args.csv}")
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


def main(argv=None) -> int:
    return asyncio.run(async_main(argv))
