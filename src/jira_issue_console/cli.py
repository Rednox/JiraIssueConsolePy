"""Simple CLI for JiraIssueConsolePy.

This uses only the standard library so the scaffold can run without extra dependencies.
"""

import argparse
import asyncio
import csv
import os
from typing import Optional, List, Any

try:
    import click
except Exception:
    click: Any = None  # type: ignore

from .core import issues
from .core.csv_export import export_cycle_time_csv
from .core.cycletime import export_cycle_time_rows
from .core.cfd import calculate_cfd_data, export_cfd_rows
from .core.json_input import load_issues_from_json
from .core.workflow_config import load_workflow_config
from .core.issue_timing import export_status_timing_rows, export_transitions_rows
from .core.issues import prepare_issues_with_transitions


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jira-issue-console")
    p.add_argument("project", help="Jira project key to list issues for")
    p.add_argument("--csv", metavar="CSV_FILE", help="Export cycle times to CSV file")
    p.add_argument(
        "--cfd",
        metavar="CSV_FILE",
        help="Export CFD (Cumulative Flow Diagram) data to CSV file",
    )
    p.add_argument(
        "--jql", help="Custom JQL query (e.g. 'priority = High AND status = Open')"
    )
    p.add_argument(
        "--input", metavar="JSON_FILE", help="JSON input file (offline mode)"
    )
    p.add_argument("--workflow", metavar="WORKFLOW_FILE", help="Workflow mapping file")
    p.add_argument(
        "--status-timing", metavar="CSV_FILE", help="Export status timing to CSV"
    )
    p.add_argument(
        "--transitions", metavar="CSV_FILE", help="Export transitions to CSV"
    )
    p.add_argument(
        "--output",
        metavar="OUTPUT_FOLDER",
        help="Output folder for all exports (generates CFD, IssueTimes, StatusTiming, and Transitions files with project key prefix)",
    )
    p.add_argument(
        "--business-days",
        action="store_true",
        help="Use business days (exclude weekends) for time calculations",
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
        if (
            args.csv
            or args.cfd
            or args.status_timing
            or args.transitions
            or args.output
        ):
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

        # Prepare issues with transitions (needed for CFD, status timing, and transitions)
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )

        # Generate filenames with project key prefix
        project_key = args.project
        cfd_file = os.path.join(args.output, f"{project_key}_CFD.csv")
        issue_times_file = os.path.join(args.output, f"{project_key}_IssueTimes.csv")
        transitions_file = os.path.join(args.output, f"{project_key}_Transitions.csv")

        # 1. Export CFD data
        cfd_data = calculate_cfd_data(issues_with_transitions, workflow=workflow)
        rows = export_cfd_rows(cfd_data)
        with open(cfd_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Day"]
                + sorted(
                    set(
                        status
                        for row in rows
                        for status in row.keys()
                        if status != "Day"
                    )
                ),
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported CFD data to {cfd_file}")

        # 2. Export status timing (as IssueTimes.csv)
        use_business_days = config.use_business_days if config else False
        holidays = config.holidays if config else set()
        rows = export_status_timing_rows(
            issues_with_transitions,
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )
        with open(issue_times_file, "w", encoding="utf-8", newline="") as f:
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
                        k
                        for k in row.keys()
                        if k not in fixed_fields and k != "Resolution"
                    )

                # Build field names: fixed fields + sorted status columns + Resolution
                fieldnames = fixed_fields + sorted(all_statuses) + ["Resolution"]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported status timing to {issue_times_file}")

        # 3. Export transitions
        rows = export_transitions_rows(issues_with_transitions, workflow=workflow)
        with open(transitions_file, "w", encoding="utf-8", newline="") as f:
            fieldnames = ["Key", "Transition", "Timestamp"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported transitions to {transitions_file}")

        return 0

    # Export cycle times if requested
    if args.csv:
        rows = export_cycle_time_rows(raw_issues, config=config)
        csv_str = export_cycle_time_csv(rows)
        if csv_str is not None:  # type narrowing
            with open(args.csv, "w", encoding="utf-8") as f:
                f.write(csv_str)
            print(f"Exported cycle times to {args.csv}")
        return 0

    # Export CFD data if requested
    if args.cfd:
        # Prepare issues with transitions for CFD calculation
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        cfd_data = calculate_cfd_data(issues_with_transitions, workflow=workflow)
        rows = export_cfd_rows(cfd_data)
        with open(args.cfd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Day"]
                + sorted(
                    set(
                        status
                        for row in rows
                        for status in row.keys()
                        if status != "Day"
                    )
                ),
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported CFD data to {args.cfd}")
        return 0

    # Export status timing if requested
    if args.status_timing:
        # Prepare issues with transitions for timing calculation
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        use_business_days = config.use_business_days if config else False
        holidays = config.holidays if config else set()
        rows = export_status_timing_rows(
            issues_with_transitions,
            workflow=workflow,
            use_business_days=use_business_days,
            holidays=holidays,
        )
        with open(args.status_timing, "w", encoding="utf-8", newline="") as f:
            if rows:
                # Get all unique status names from all rows
                all_statuses_2: set[str] = set()
                for row in rows:
                    all_statuses_2.update(k for k in row.keys() if k != "key")
                fieldnames = ["key"] + sorted(all_statuses_2)
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        print(f"Exported status timing to {args.status_timing}")
        return 0

    # Export transitions if requested
    if args.transitions:
        # Prepare issues with transitions for export
        issues_with_transitions = prepare_issues_with_transitions(
            raw_issues, workflow=None
        )
        rows = export_transitions_rows(issues_with_transitions, workflow=workflow)
        with open(args.transitions, "w", encoding="utf-8", newline="") as f:
            fieldnames = ["Key", "Transition", "Timestamp"]
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
    @click.option("--csv", "csv_file", help="Export cycle times to CSV file")
    @click.option(
        "--cfd",
        "cfd_file",
        help="Export CFD (Cumulative Flow Diagram) data to CSV file",
    )
    @click.option("--jql", "jql", help="Custom JQL query")
    @click.option("--input", "input_file", help="JSON input file (offline mode)")
    @click.option("--workflow", "workflow_file", help="Workflow mapping file")
    @click.option(
        "--status-timing", "status_timing_file", help="Export status timing to CSV"
    )
    @click.option("--transitions", "transitions_file", help="Export transitions to CSV")
    @click.option(
        "--output",
        "output_folder",
        help="Output folder for all exports (generates CFD, IssueTimes, StatusTiming, and Transitions files with project key prefix)",
    )
    @click.option(
        "--business-days",
        "business_days",
        is_flag=True,
        help="Use business days for time calculations",
    )
    def app(
        project: str,
        csv_file: Optional[str],
        cfd_file: Optional[str],
        jql: Optional[str],
        input_file: Optional[str],
        workflow_file: Optional[str],
        status_timing_file: Optional[str],
        transitions_file: Optional[str],
        output_folder: Optional[str],
        business_days: bool,
    ) -> int:
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
        if output_folder:
            argv.extend(["--output", output_folder])
        if business_days:
            argv.append("--business-days")
        rc = asyncio.run(async_main(argv))
        if rc:
            raise SystemExit(rc)
        return rc or 0
else:
    # Provide a minimal placeholder so imports don't fail in environments without click
    app: Any = None  # type: ignore
