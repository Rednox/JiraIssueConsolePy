"""Simple CLI for JiraIssueConsolePy.

This uses only the standard library so the scaffold can run without extra dependencies.
"""

import argparse
import asyncio
import csv
import os
from datetime import date, timedelta
from typing import Optional, List, Any

try:
    import click
except Exception:
    click: Any = None  # type: ignore

from .core import issues
from .core.cfd import calculate_cfd_data, export_cfd_rows
from .core.json_input import load_issues_from_json
from .core.workflow_config import load_workflow_config
from .core.issue_timing import export_issue_times_rows, export_transitions_rows
from .core.issues import prepare_issues_with_transitions
from .core.excel_export import export_to_excel, get_file_extension


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jira-issue-console")
    p.add_argument("project", help="Jira project key to list issues for")
    p.add_argument(
        "--issue-times",
        metavar="FILE",
        help="Export issue times (elapsed times from start to finish and total time spent in each status per issue)",
    )
    p.add_argument(
        "--cfd",
        metavar="FILE",
        help="Export CFD (Cumulative Flow Diagram) data - daily count of status changes by status for the last 5 years",
    )
    p.add_argument(
        "--jql", help="Custom JQL query (e.g. 'priority = High AND status = Open')"
    )
    p.add_argument(
        "--input", metavar="JSON_FILE", help="JSON input file (offline mode)"
    )
    p.add_argument("--workflow", metavar="WORKFLOW_FILE", help="Workflow mapping file")
    p.add_argument(
        "--transitions",
        metavar="FILE",
        help="Export transitions (complete log of status changes per feature with associated timestamps)",
    )
    p.add_argument(
        "--output",
        metavar="OUTPUT_FOLDER",
        help="Output folder for all exports (generates CFD, IssueTimes, and Transitions files with project key prefix)",
    )
    p.add_argument(
        "--business-days",
        action="store_true",
        help="Use business days (exclude weekends) for time calculations",
    )
    p.add_argument(
        "--format",
        choices=["csv", "excel"],
        default="csv",
        help="Output format for exports (csv or excel). Default is csv.",
    )
    return p


async def async_main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Create config object for business days calculations
    from .config import Config

    config = None
    if args.business_days:
        config = Config(
            jira_base_url="",  # Not needed for CLI-only usage
            jira_user=None,
            jira_api_token=None,
            use_business_days=True,
            holidays=set(),
        )

    # Load workflow config if provided
    workflow = None
    if args.workflow:
        workflow = load_workflow_config(args.workflow)

    # Load issues from JSON file (offline mode) or from Jira API
    if args.input:
        # Offline mode: load from JSON file
        raw_issues = load_issues_from_json(args.input)
    else:
        # Online mode: fetch from Jira API
        # For display mode, use simplified format
        # For export modes, we need full format with changelog
        if args.issue_times or args.cfd or args.transitions or args.output:
            # Need full issue data for exports - fetch with expand=changelog
            from . import jira_client

            if getattr(args, "jql", None):
                raw_issues = await jira_client.fetch_issues(args.project, jql=args.jql)
            else:
                raw_issues = await jira_client.fetch_issues(args.project)
        else:
            # Simple display mode - use simplified format
            if getattr(args, "jql", None):
                items = await issues.list_issues(args.project, jql=args.jql)
            else:
                items = await issues.list_issues(args.project)
            # Print a simple table header and rows
            header_key = "KEY"
            header_summary = "SUMMARY"
            print(f"{header_key:<16} {header_summary}")
            print(f"{'-' * 16} {'-' * 40}")
            for it in items:
                key = it.get("key", "")
                summary = it.get("summary", "") or ""
                print(f"{key:<16} {summary}")
            return 0

    # Handle --output parameter (generates all export files)
    if args.output:
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)

        # Prepare issues with transitions (needed for CFD, issue timing, and transitions)
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )

        # Get file extension based on format
        file_ext = get_file_extension(args.format)

        # Generate filenames with project key prefix
        project_key = args.project
        cfd_file = os.path.join(args.output, f"{project_key}_CFD{file_ext}")
        issue_times_file = os.path.join(
            args.output, f"{project_key}_IssueTimes{file_ext}"
        )
        transitions_file = os.path.join(
            args.output, f"{project_key}_Transitions{file_ext}"
        )

        # 1. Export CFD data (for the last 5 years)
        five_years_ago = date.today() - timedelta(days=5 * 365)
        cfd_data = calculate_cfd_data(
            issues_with_transitions, workflow=workflow, start_date=five_years_ago
        )
        rows = export_cfd_rows(cfd_data)
        fieldnames_cfd = ["Day"] + sorted(
            set(status for row in rows for status in row.keys() if status != "Day")
        )

        if args.format == "excel":
            export_to_excel(rows, cfd_file, fieldnames_cfd)
        else:
            with open(cfd_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_cfd)
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported CFD data to {cfd_file}")

        # 2. Export issue timing (as IssueTimes)
        use_business_days = config.use_business_days if config else False
        holidays = config.holidays if config else set()
        rows = export_issue_times_rows(
            issues_with_transitions,
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )

        if rows:
            # Define fixed field order for IssueTimes format
            fixed_fields = [
                "Project",
                "Group",
                "Key",
                "Issuetype",
                "Status",
                "Created Date",
                "Component",
                "Category",
                "First Date",
                "Implementation Date",
                "Closed Date",
            ]

            # Get all unique status columns (excluding fixed and Resolution)
            all_statuses: set[str] = set()
            for row in rows:
                all_statuses.update(
                    k for k in row.keys() if k not in fixed_fields and k != "Resolution"
                )

            # Build field names: fixed fields + sorted status columns + Resolution
            fieldnames = fixed_fields + sorted(all_statuses) + ["Resolution"]

            if args.format == "excel":
                export_to_excel(rows, issue_times_file, fieldnames)
            else:
                with open(issue_times_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
        print(f"Exported issue times to {issue_times_file}")

        # 3. Export transitions
        rows = export_transitions_rows(issues_with_transitions, workflow=workflow)
        fieldnames_trans = ["Key", "Transition", "Timestamp"]

        if args.format == "excel":
            export_to_excel(rows, transitions_file, fieldnames_trans)
        else:
            with open(transitions_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames_trans, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported transitions to {transitions_file}")

        return 0

    # Export issue times if requested
    if args.issue_times:
        # Prepare issues with transitions for timing calculation
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        use_business_days = config.use_business_days if config else False
        holidays = config.holidays if config else set()
        rows = export_issue_times_rows(
            issues_with_transitions,
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )

        if rows:
            # Define fixed field order for IssueTimes format
            fixed_fields = [
                "Project",
                "Group",
                "Key",
                "Issuetype",
                "Status",
                "Created Date",
                "Component",
                "Category",
                "First Date",
                "Implementation Date",
                "Closed Date",
            ]

            # Get all unique status columns (excluding fixed and Resolution)
            all_statuses_set: set[str] = set()
            for row in rows:
                all_statuses_set.update(
                    k for k in row.keys() if k not in fixed_fields and k != "Resolution"
                )

            # Build field names: fixed fields + sorted status columns + Resolution
            fieldnames = fixed_fields + sorted(all_statuses_set) + ["Resolution"]

            if args.format == "excel":
                export_to_excel(rows, args.issue_times, fieldnames)
            else:
                with open(args.issue_times, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
        print(f"Exported issue times to {args.issue_times}")
        return 0

    # Export CFD data if requested
    if args.cfd:
        # Prepare issues with transitions for CFD calculation
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        # Calculate CFD for the last 5 years
        five_years_ago = date.today() - timedelta(days=5 * 365)
        cfd_data = calculate_cfd_data(
            issues_with_transitions, workflow=workflow, start_date=five_years_ago
        )
        rows = export_cfd_rows(cfd_data)
        fieldnames = ["Day"] + sorted(
            set(status for row in rows for status in row.keys() if status != "Day")
        )

        if args.format == "excel":
            export_to_excel(rows, args.cfd, fieldnames)
        else:
            with open(args.cfd, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported CFD data to {args.cfd}")
        return 0

    # Export transitions if requested
    if args.transitions:
        # Prepare issues with transitions for export
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        rows = export_transitions_rows(issues_with_transitions, workflow=workflow)
        fieldnames = ["Key", "Transition", "Timestamp"]

        if args.format == "excel":
            export_to_excel(rows, args.transitions, fieldnames)
        else:
            with open(args.transitions, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported transitions to {args.transitions}")
        return 0

    # If no export flag was provided but we're in offline mode, print issues
    header_key = "KEY"
    header_summary = "SUMMARY"
    print(f"{header_key:<16} {header_summary}")
    print(f"{'-' * 16} {'-' * 40}")
    for it in raw_issues:
        key = it.get("key", "")
        fields = it.get("fields", {})
        summary = fields.get("summary", "") or ""
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
    @click.option(
        "--issue-times",
        "issue_times_file",
        help="Export issue times (elapsed times from start to finish and total time spent in each status per issue)",
    )
    @click.option(
        "--cfd",
        "cfd_file",
        help="Export CFD (Cumulative Flow Diagram) data - daily count of status changes by status for the last 5 years",
    )
    @click.option("--jql", "jql", help="Custom JQL query")
    @click.option("--input", "input_file", help="JSON input file (offline mode)")
    @click.option("--workflow", "workflow_file", help="Workflow mapping file")
    @click.option(
        "--transitions",
        "transitions_file",
        help="Export transitions (complete log of status changes per feature with associated timestamps)",
    )
    @click.option(
        "--output",
        "output_folder",
        help="Output folder for all exports (generates CFD, IssueTimes, and Transitions files with project key prefix)",
    )
    @click.option(
        "--business-days",
        "business_days",
        is_flag=True,
        help="Use business days for time calculations",
    )
    @click.option(
        "--format",
        "format_type",
        type=click.Choice(["csv", "excel"]),
        default="csv",
        help="Output format for exports (csv or excel). Default is csv.",
    )
    def app(
        project: str,
        issue_times_file: Optional[str],
        cfd_file: Optional[str],
        jql: Optional[str],
        input_file: Optional[str],
        workflow_file: Optional[str],
        transitions_file: Optional[str],
        output_folder: Optional[str],
        business_days: bool,
        format_type: str,
    ) -> int:
        """Compatibility Click command used by tests (runner.invoke(app, args))."""
        argv: List[str] = [project]
        if issue_times_file:
            argv.extend(["--issue-times", issue_times_file])
        if cfd_file:
            argv.extend(["--cfd", cfd_file])
        if jql:
            argv.extend(["--jql", jql])
        if input_file:
            argv.extend(["--input", input_file])
        if workflow_file:
            argv.extend(["--workflow", workflow_file])
        if transitions_file:
            argv.extend(["--transitions", transitions_file])
        if output_folder:
            argv.extend(["--output", output_folder])
        if business_days:
            argv.append("--business-days")
        if format_type != "csv":
            argv.extend(["--format", format_type])
        rc = asyncio.run(async_main(argv))
        if rc:
            raise SystemExit(rc)
        return rc or 0
else:
    # Provide a minimal placeholder so imports don't fail in environments without click
    app: Any = None  # type: ignore
