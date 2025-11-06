# VSCode Testing Guide

This guide explains how to set up and run tests locally in VSCode without needing network connectivity.

## Prerequisites

- Python 3.9+ installed
- VSCode with Python extension installed
- All test files and fixtures are included in the repository

## Setup Steps

### 1. Create Virtual Environment

Open the VSCode integrated terminal and run:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies (requires network connection)
pip install -r requirements.txt -r dev-requirements.txt
```

**Note**: This step requires internet access. If you're offline:
- Install dependencies on a machine with network access
- Copy the `.venv` folder to your offline machine
- Or use a local PyPI mirror/cache

### 3. Configure VSCode Python Settings

Create/update `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests",
        "-v"
    ],
    "python.envFile": "${workspaceFolder}/.env.test"
}
```

### 4. Create Test Environment File

Create `.env.test` in the project root:

```bash
# Required for tests (dummy values work for offline tests)
JIRA_BASE_URL=https://example.atlassian.net
JIRA_USER=test_user
JIRA_API_TOKEN=dummy_token
PYTHONPATH=src
```

## Running Tests

### Option 1: Using Makefile (Recommended)

```bash
# Run all tests
make test

# Run with coverage
PYTHONPATH=src .venv/bin/pytest -v --cov=src --cov-report=term-missing

# Run specific test file
PYTHONPATH=src .venv/bin/pytest tests/unit/test_workflow_config.py -v

# Run specific test
PYTHONPATH=src .venv/bin/pytest tests/unit/test_workflow_config.py::test_parse_simple_format -v
```

### Option 2: Using VSCode Test Explorer

1. Open VSCode Command Palette (Cmd/Ctrl+Shift+P)
2. Type "Python: Configure Tests"
3. Select "pytest"
4. The Test Explorer icon will appear in the Activity Bar
5. Click it to see all tests
6. Click the play button next to any test to run it

### Option 3: Using VSCode Tasks

The repository includes predefined tasks in `.vscode/tasks.json`:

1. Open Command Palette (Cmd/Ctrl+Shift+P)
2. Type "Run Task"
3. Select from:
   - **Test All** - Run all tests
   - **Test Current File** - Run tests in active file
   - **Lint** - Run ruff linter
   - **Type Check** - Run mypy type checker

### Option 4: From Terminal

```bash
# Activate virtual environment first
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Set PYTHONPATH
export PYTHONPATH=src  # or set PYTHONPATH=src on Windows

# Run all tests
pytest -v

# Run unit tests only
pytest tests/unit/ -v

# Run acceptance tests only
pytest tests/acceptance/ -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests matching a pattern
pytest -k "workflow" -v
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Fast, isolated tests
- No network calls (all mocked)
- Test individual functions/classes
- Run frequently during development

### Acceptance Tests (`tests/acceptance/`)
- BDD-style tests using pytest-bdd
- Test CLI behavior end-to-end
- Use fixtures and mocked responses
- Validate user stories

## Offline Testing

All tests are designed to work offline:

1. **Mocked HTTP Calls**: Uses `respx` to mock Jira API responses
2. **Test Fixtures**: Sample data in `tests/fixtures/`
3. **Example Files**: Real JSON exports in `examples/`
4. **No External Dependencies**: All test data is in the repository

Example test data locations:
- `tests/fixtures/example.json` - Sample Jira export
- `examples/workflow_example.txt` - Example workflow file

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src
# Or run with pytest's python path option
pytest --pythonpath=src
```

### VSCode Not Finding Tests

1. Check Python interpreter is set to `.venv`
2. Reload VSCode window (Cmd/Ctrl+Shift+P → "Reload Window")
3. Check Output → Python Test Log for errors

### Tests Fail with Network Errors

Tests should NOT require network. If they do:
- Check that `respx` mocks are properly configured
- Ensure test fixtures exist
- Verify environment variables are set

### Missing pytest-bdd

If you see `ModuleNotFoundError: No module named 'pytest_bdd'`:
```bash
pip install pytest-bdd>=6.1.0
# Or reinstall dev requirements
pip install -r dev-requirements.txt
```

## Linting and Type Checking

### Lint with Ruff

```bash
# Check for issues
.venv/bin/ruff check src tests

# Auto-fix issues
.venv/bin/ruff check --fix src tests

# Format code
.venv/bin/ruff format src tests
```

### Type Check with Mypy

```bash
PYTHONPATH=src .venv/bin/mypy src
```

## CI/CD Validation

To validate changes locally before pushing:

```bash
# Run the same checks as CI
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
PYTHONPATH=src .venv/bin/mypy src
PYTHONPATH=src .venv/bin/pytest -v --cov=src
```

## Quick Reference

```bash
# One-time setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r dev-requirements.txt

# Daily development
source .venv/bin/activate
export PYTHONPATH=src
pytest -v                    # Run tests
pytest -k "test_name" -v     # Run specific test
ruff check src tests         # Lint
mypy src                     # Type check
```

## VSCode Keyboard Shortcuts

- `Cmd/Ctrl+Shift+P` → "Test: Run All Tests"
- `Cmd/Ctrl+Shift+P` → "Test: Run Test at Cursor"
- `Cmd/Ctrl+Shift+P` → "Test: Debug Test at Cursor"
- `Cmd/Ctrl+Shift+P` → "Python: Run Selection/Line in Python Terminal"

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-bdd documentation](https://pytest-bdd.readthedocs.io/)
- [VSCode Python Testing](https://code.visualstudio.com/docs/python/testing)
