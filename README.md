# JiraIssueConsolePy

This repository is a Python port of the C# project `Jaegerfeld/JiraIssueConsole`, providing a command-line tool for querying Jira issues and calculating cycle times.

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
python -m jira_issue_console PROJ --csv cycle_times.csv  # export cycle times
python -m jira_issue_console PROJ --jql "priority = High"  # filter with JQL
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
