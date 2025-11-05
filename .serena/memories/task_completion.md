# Task Completion Checklist

Before considering a task complete:

1. Code Quality
   - [ ] All tests pass (unit and acceptance)
   - [ ] Type hints are complete and mypy passes
   - [ ] Ruff linting passes with no errors
   - [ ] Code follows project style guide
   - [ ] Docstrings are complete and accurate

2. Testing
   - [ ] Unit tests cover new functionality
   - [ ] Edge cases are tested
   - [ ] Integration tests if needed
   - [ ] Acceptance tests for user features

3. Documentation
   - [ ] Updated relevant documentation
   - [ ] Added inline comments for complex logic
   - [ ] Updated README if user-facing changes

4. Review
   - [ ] Self-review complete
   - [ ] No debug code or print statements
   - [ ] No unnecessary commented code
   - [ ] All TODOs addressed

5. Run Commands
```bash
# Must run and pass:
make test
make lint
make typecheck

# Or individually:
PYTHONPATH=src pytest
ruff src tests
mypy src
```