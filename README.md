# JiraIssueConsolePy

This repository is a Python port of the C# project `Jaegerfeld/JiraIssueConsole`, providing a command-line tool for querying Jira issues and analyzing workflow metrics like cycle times, cumulative flow, and status transitions.

## Quick Start

```bash
# Install from source (requires Python 3.9+)
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set up Jira credentials in environment
export JIRA_BASE_URL="https://your-jira-instance.com"
export JIRA_USER="your-username"
export JIRA_API_TOKEN="your-api-token"

# Run the CLI
python -m jira_issue_console PROJ  # list open issues for project
python -m jira_issue_console PROJ --jql "priority = High"  # filter with JQL

# Export cycle time metrics
python -m jira_issue_console PROJ --csv cycle_times.csv  # basic cycle times
python -m jira_issue_console PROJ --cfd cfd.csv  # cumulative flow diagram data
python -m jira_issue_console PROJ --status-timing status_times.csv  # time in each status
python -m jira_issue_console PROJ --transitions transitions.csv  # status transition history

# Use business days for calculations
python -m jira_issue_console PROJ --business-days --csv cycle_times.csv

# Customize workflow status mapping
python -m jira_issue_console PROJ --workflow workflow.txt --csv cycle_times.csv
```

## Features

### Issue Analysis Modes
- Direct Jira API integration for live data
- Offline mode using pre-exported JSON files
- Filter using JQL queries (API mode)
- Display key issue fields and status

### Security Notes

- Store credentials in environment variables, never in code or config files
- Use API tokens instead of passwords when possible
- When exporting JSON data:
  - Remove sensitive information (assignees, custom fields, etc.)
  - Don't commit raw Jira exports to version control
  - Set appropriate file permissions (e.g., `chmod 600 exports/*.json`)
  - Validate JSON input structure (the tool enforces required fields)
  - Sanitize JSON exports before sharing (see jq example below)
  - Place JSON files in secure directories with restricted access
- Keep workflow mapping files free of sensitive data
- JSON input security checks:
  - File permissions are validated (warnings for group/world readable)
  - Structure validation ensures proper Jira issue format
  - Protection against directory traversal and symlink attacks
  - Basic sanitization of issue fields

### Offline Mode
Process pre-exported Jira data from JSON files:
```bash
# Export issues from Jira API to JSON (using jq to filter sensitive fields)
curl -u user:token "https://your-jira/rest/api/2/search?jql=project=PROJ" | \
  jq 'del(.issues[].fields | select(.description, .environment, .customfields))' \
  > sanitized.json

# Analyze the exported data
python -m jira_issue_console PROJ --input example.json --csv cycle_times.csv
python -m jira_issue_console PROJ --input example.json --cfd cfd.csv
python -m jira_issue_console PROJ --input example.json --transitions transitions.csv
```

Example JSON format:
```json
{
    "issues": [
        {
            "id": "10001",
            "key": "PROJ-1",
            "fields": {
                "summary": "Example issue",
                "created": "2023-01-01T10:00:00.000+0000",
                "status": {"name": "Open"},
                "changelog": {
                    "histories": [
                        {
                            "created": "2023-01-02T14:00:00.000+0000",
                            "items": [
                                {
                                    "field": "status",
                                    "toString": "In Progress"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    ]
}
```

### Cycle Time Analysis
- Calculate cycle time between issue creation and resolution
- Support for calendar days or business days
- Configurable holiday exclusions
- Time tracking in each workflow status

### Workflow Metrics
- Cumulative Flow Diagram (CFD) data generation
- Status transition history and timing
- Configurable workflow status mapping
- Detailed timing breakdowns

### Data Export
Several CSV export formats available:
- `cycle_times.csv` - Basic cycle time metrics
- `cfd.csv` - Daily counts for Cumulative Flow Diagram
- `status_timing.csv` - Time spent in each workflow status
- `transitions.csv` - Complete status transition history

### Workflow Configuration
Define custom workflow mappings to normalize status names:
```text
# workflow.txt example
In Review -> In Progress
Testing -> In Progress
Ready for QA -> In Progress
```

## Development Setup

The project uses pytest for testing, ruff for linting, and mypy for type checking. A Makefile is provided for common development tasks.

```bash
# Create virtualenv and install all dependencies (including dev tools)
make setup

# Run tests
make test
make test-watch  # watch mode with pytest-watch

# Quality checks
make lint        # run ruff
make typecheck   # run mypy

# Clean up
make clean
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r dev-requirements.txt
PYTHONPATH=src pytest
```

### Pre-push quality gate

This repo uses pre-commit to enforce a strict pre-push gate that catches issues the CI would otherwise find:

- Ruff (lint + format check)
- Mypy (type checking)
- Pytest with warnings treated as errors (`-W error`)
- A smoke CLI run in offline mode that fails if any warnings/errors/tracebacks appear in the console output

Enable hooks once locally:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

Run the pre-push checks manually any time:

```bash
pre-commit run --all-files
pre-commit run --hook-stage push --all-files
```

If any check fails, fix it before pushing. Treat a clean console (no warnings) as mandatory, alongside lint/type/tests.

### VS Code Settings

For VS Code users, the repository includes tasks for running tests, lint, and type checks. The tasks use `python3 -m ...` to ensure tools are run through the Python interpreter.

To run tasks:
1. Open the Command Palette (Cmd/Ctrl+Shift+P)
2. Type "Run Task" and select from:
   - Test All
   - Test Current File
   - Test Watch
   - Lint
   - Type Check

## License

TBD
