# Updated Copilot Instructions for JiraIssueConsolePy

## Project Scope Update

### Core Features
The Python port should fully implement:
- All workflow state processing including aliases and deprecated status mapping
- Complete status transition history
- CFD (Cumulative Flow Diagram) report generation
- Idle time tracking
- Component/project field support
- Parent issue (epic) linking

### Model Architecture 
1. Core Domain Models (`src/jira_issue_console/models/`)
   - `workflow.py`: Workflow state machine with transitions
   - `issue.py`: Jira issue with fields and history
   - `status.py`: Status with timing info
   - `report.py`: Report data structures

2. Business Logic (`src/jira_issue_console/core/`)
   - `workflow_processor.py`: Status transition processing
   - `time_calculator.py`: Timing calculations
   - `cfd_generator.py`: CFD report generation
   - `csv_exporter.py`: Report export handling

### Testing Strategy
1. Unit Tests
   - Test each component in isolation
   - Mock external dependencies
   - Focus on business logic accuracy

2. Integration Tests
   - Test component interactions
   - Use recorded fixtures
   - Focus on data flow

3. Acceptance Tests
   - Feature files matching C# behaviors
   - CLI workflow testing
   - End-to-end scenarios

### DevOps Requirements
1. CI Pipeline
   - Run tests on Python 3.10+
   - Enforce type checking
   - Check test coverage
   - Security scanning

2. Release Process
   - Semantic versioning
   - Automated changelog
   - PyPI publishing

### Security Standards
1. Input Validation
   - Config file validation
   - JSON input sanitization
   - Path traversal prevention

2. API Security  
   - Rate limiting
   - Request timeouts
   - Error handling

## Development Workflow

### TDD Process
1. Write failing test
2. Implement minimal code
3. Refactor
4. Update documentation

### BDD Process  
1. Write feature file
2. Implement steps
3. Add fixtures
4. Test acceptance criteria

### Code Review Checklist
- Unit test coverage
- Type hints complete
- Documentation updated
- Security reviewed
- Error handling proper