# Code Style and Conventions

## Python Conventions
- Use Python 3.9+ features and type hints
- Follow PEP 8 style guide
- Use async/await for I/O operations

## Project Structure
- Package code under `src/jira_issue_console/`
- Tests under `tests/` (unit/, acceptance/)
- Core business logic in `core/` module
- HTTP client in `jira_client.py`
- Data models in `models/`

## Type Hints
- All public functions must have type hints
- Use Optional[] for nullable parameters
- Use TypeVar for generic type parameters

## Testing
- Unit tests with pytest
- BDD/acceptance tests with feature files
- Async test support via pytest-asyncio
- High test coverage expected

## Documentation
- Docstrings for all public functions (Google style)
- README.md for user documentation
- Comments for complex algorithms
- Type hints as documentation

## Error Handling
- Use custom exceptions for domain errors
- Log errors appropriately
- Clear error messages for CLI users