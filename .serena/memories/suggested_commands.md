# Development Commands

## Project Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt -r dev-requirements.txt
```

## Testing Commands
```bash
# Run all tests
make test
PYTHONPATH=src pytest

# Run tests for current file
PYTHONPATH=src pytest path/to/test_file.py

# Watch mode
make test-watch
PYTHONPATH=src pytest-watch -- -v -p no:warnings

# Run specific test
pytest path/to/test_file.py::test_function -v
```

## Quality Checks
```bash
# Lint with ruff
make lint
ruff src tests

# Type check with mypy
make typecheck
mypy src

# Run all checks
make check  # runs lint & type check
```

## Running the CLI
```bash
# Set up environment
export JIRA_BASE_URL="https://your-jira-instance.com"
export JIRA_USER="your-username" 
export JIRA_API_TOKEN="your-api-token"

# Run commands
python -m jira_issue_console PROJ
python -m jira_issue_console PROJ --csv cycle_times.csv
python -m jira_issue_console PROJ --jql "priority = High"
```

## VS Code Tasks
Available via Command Palette (Cmd/Ctrl+Shift+P):
- Test All
- Test Current File  
- Test Watch
- Lint
- Type Check

## Git Commands
```bash
# Basic workflow
git status
git add .
git commit -m "message"
git push

# Feature branches
git checkout -b feature/name
git push -u origin feature/name
```

## Utility Commands (macOS)
```bash
# Directory operations
ls -la
cd path/to/dir
pwd

# File operations  
cat file.txt
head -n 20 file.txt
tail -f file.txt

# Search
find . -name "*.py"
grep -r "pattern" .
```