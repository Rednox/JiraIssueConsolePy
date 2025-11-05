# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] - 2025-11-06

### Added
- Core business logic modules:
  - CFD (Cumulative Flow Diagram) calculation and export
  - Issue timing and status transition tracking
  - Workflow configuration parsing and status mapping
  - JSON offline input support
  - CSV export utilities with proper line terminator handling
  - Business days calculation
- Test infrastructure:
  - Comprehensive unit tests (62 passing)
  - BDD acceptance tests with pytest-bdd
  - Test fixtures and conftest setup
  - Respx mock compatibility layer
- CLI enhancements:
  - CFD export (`--cfd`)
  - Argument parsing for workflow, input, status-timing, transitions
  - Click wrapper for test compatibility
- Documentation:
  - Updated README with CFD documentation
  - Feature files for BDD scenarios
  - Copilot instructions for AI-assisted development

### Fixed
- Type checking: All mypy errors resolved (strict mode enabled)
  - Fixed mutable dataclass defaults
  - Added proper type annotations across codebase
  - Corrected import paths for WorkflowConfig
- Core logic fixes:
  - CFD calculation now properly tracks cumulative state over date ranges
  - Issue transitions correctly extract initial status from changelog
  - Workflow config auto-populates group names when statuses omitted
  - CSV export ensures LF line terminators for cross-platform consistency
- Test infrastructure:
  - Added shared pytest fixtures via conftest.py
  - Fixed pytest-bdd step definitions for docstring parameters
  - Added respx MockRouter.Response compatibility shim
  - Improved VS Code tasks.json for better mypy integration

### Changed
- Dependencies: Added httpx, respx, pytest-bdd, click to dev requirements
- CI/CD: Enhanced GitHub Actions workflow with better error reporting
- Configuration: Updated pyproject.toml with package metadata and classifiers

### Known Issues
- 7 acceptance tests fail due to unimplemented CLI features:
  - `--input` JSON offline mode (parsing only)
  - `--workflow` workflow mapping integration
  - `--status-timing` status timing export
  - `--transitions` transitions export
  These features have argument parsing but need implementation in async_main()

### Technical Details
- Python compatibility: 3.9+
- Test coverage: 62 passing, 1 skipped, 7 failing (unimplemented features)
- Type safety: 100% mypy compliance with strict mode
- Code quality: Clean ruff (linter) results
