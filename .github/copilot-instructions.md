<!--
  Copilot / AI agent instructions for JiraIssueConsolePy
  Purpose: guide AI agents to port the C# project
  https://github.com/Jaegerfeld/JiraIssueConsole into a high-quality Python equivalent.
  Update any placeholders below after a full repo scan.
-->

# Copilot / AI agent instructions — JiraIssueConsolePy

Purpose
- Port the C# project `Jaegerfeld/JiraIssueConsole` to Python while preserving behavior
  parity for business logic and CLI UX. Use TDD for core logic and BDD for CLI/acceptance tests.

Where to look and mapping guidance
- Start by reading the C# project source (link above). Produce `docs/mapping.md` that maps
  each C# class or public method to the Python module/function you plan to create.
- Suggested Python module mapping:
  - C# Program/CLI => `src/jira_issue_console/__main__.py` and `src/jira_issue_console/cli.py`
  - Business logic => `src/jira_issue_console/core/` (pure code, TDD)
  - Jira HTTP integration => `src/jira_issue_console/jira_client.py` (network wrapper)
  - Models/DTOs => `src/jira_issue_console/models/` (dataclasses or pydantic models)
  - Tests => `tests/unit/`, `tests/integration/`, `tests/acceptance/`

Developer workflows (TDD/BDD + DevOps)
- TDD for domain logic: write failing unit tests first (pytest), implement minimal code, refactor.
- BDD for features/CLI: write feature files (pytest-bdd or behave) that represent C# acceptance tests.
- Local quickstart:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # zsh
  pip install -r requirements.txt
  pytest -q
  ```
- Recommended dev tools: `pytest`, `pytest-mock`, `requests-mock` or `respx` (async), `httpx`,
  `black`, `ruff` (or flake8), `mypy`, `pre-commit`.

Project conventions (enforceable rules for contributors)
- Config via environment variables: `JIRA_BASE_URL`, `JIRA_USER`, `JIRA_API_TOKEN`.
- Code layout: package under `src/`, tests under `tests/`.
- Type hints on public functions and dataclasses for models.
- Network calls isolated in `jira_client.py`; business logic must be independent of network.
- Use `logging` for app logs; CLI may write to stdout/stderr.

Integration points
- Jira REST API — build URLs from `JIRA_BASE_URL` and use token/basic auth headers.
- Wrap HTTP interactions to allow unit-level mocking; prefer `httpx` for sync/async flexibility.

Roadmap (phases & timeline suggestions)
- Phase 0 — Discovery & mapping (3 days)
  - Clone C# repo, extract behaviors, create `docs/mapping.md` with prioritized features.
- Phase 1 — Scaffold & CI (4–7 days)
  - Create Python project skeleton (`pyproject.toml` or `requirements.txt`, package, tests),
    add GitHub Actions CI (lint, type-check, tests), pre-commit hooks.
- Phase 2 — Core port via TDD (2–3 weeks)
  - Implement domain models and core business behavior with unit tests first.
- Phase 3 — Integrations + CLI + BDD acceptance (1–2 weeks)
  - Implement `jira_client`, CLI glue, and feature tests that match C# acceptance scenarios.
- Phase 4 — QA, docs & release (3–5 days)
  - Integration tests, documentation, release candidate and tagging.

Execution plan (detailed tasks)
1) Discovery (deliverable: `docs/mapping.md`)
   - List all C# public classes and methods used by the CLI.
   - Extract acceptance scenarios from C# tests or readme/examples.

2) Scaffold repository
   - Create `pyproject.toml` with project metadata and dev dependencies (`pytest`, `black`, `ruff`, `mypy`).
   - Create `src/jira_issue_console/` and `tests/` structure.
   - Add `.github/workflows/ci.yml` with jobs: lint, type-check, unit-tests, acceptance-smoke.
   - Add `pre-commit` config.

3) First TDD story (example: fetch and transform issues)
   - Write unit tests that define expected transformation/filters (matching C# logic).
   - Implement `src/jira_issue_console/core/issues.py` to pass tests.
   - Add type hints and docstrings.

4) Implement `jira_client` behind an interface
   - Provide a simple sync implementation using `requests` or `httpx`.
   - Ensure methods return plain dicts or model instances that core logic consumes.
   - Add mocks for unit tests.

5) CLI and BDD acceptance
   - Write feature(s) for CLI user flows (list, filter, export) using pytest-bdd or behave.
   - Implement the CLI entrypoint and wiring so feature tests run against mocked responses.

6) Integration testing & hardening
   - Add optional integration tests that run against a staging Jira or use recorded fixtures.
   - Add retry/backoff and clear error messages for network failures.

7) Release and automation
   - Create a release workflow that builds artifacts and optionally publishes to PyPI.

Acceptance criteria
- Unit tests for core logic with >90% coverage for that package (or agreed threshold).
- BDD acceptance tests that mirror original C# behavior pass on CI.
- PRs must pass lint, type-check, and tests before merge.

BDD/TDD process notes
- TDD: short cycles (day or less). Tests are the contract.
- BDD: write readable scenarios derived from C# acceptance examples.
- Use fixtures to provide deterministic mock responses for Jira API.
 - Test completeness gate before final PR: ensure all BDD feature scenarios have step implementations and are included in the test run (no missing or commented-out scenarios), and that the full pytest suite passes with no unexpected xfail/skip. Avoid adding new tests marked xfail unless a tracking issue exists and is referenced in the test.
 - Zero bug policy: for every reported or discovered bug, first add a failing unit/BDD test that reproduces it, commit the test, then implement the minimal fix to make it pass. Keep the regression test permanently to prevent reoccurrence.

DevOps recommendations
- CI: GitHub Actions matrix for Python versions (3.10, 3.11), run lint/type/tests.
- Add codecov/coverage reporting.
- Enforce branch protection rules that require CI green before merging.
- **Always validate CI checks before pushing to a PR**: Run `ruff check`, `ruff format --check`, 
  `mypy src`, and `bandit` locally to ensure all quality checks pass before pushing changes.
  This prevents wasting CI resources and ensures high-quality code submissions.
 - **Before pushing, inspect console output for errors/warnings**: Run representative local flows (e.g., key CLI commands and the full pytest suite) and carefully review the terminal output for any errors, warnings, unawaited coroutine messages, or stack traces. If anything shows up, **fix it before pushing**. Treat a clean console (no errors/warnings) as a gate alongside lint/type/tests.

When to ask maintainers
- If a C# behavior is ambiguous, request the specific C# file/line or a sample CLI session
  showing the expected output.

Repo map (maintainer: fill exact paths)
- ENTRYPOINT: `src/jira_issue_console/__main__.py`
- DEPENDENCIES: `pyproject.toml` or `requirements.txt`
- TESTS: `tests/` (`tests/unit/`, `tests/integration/`, `tests/acceptance/`)
- DOCS: `docs/mapping.md`, `README.md`

Next actions I can take now
- Re-scan the workspace and scaffold the project (create `pyproject.toml`, `src/`, `tests/`, CI).
- Or start the first TDD story by creating a failing test for a chosen behavior from the C# project and
  implement the minimal Python code to satisfy it.

If you'd like me to proceed with scaffolding or start a TDD story, tell me which behavior to port first
(e.g., "list open issues for a project" or "export cycle time per issue").

-- end
