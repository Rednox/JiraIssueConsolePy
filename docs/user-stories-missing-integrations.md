# User Stories for Missing CLI Integrations

**STATUS: ALL COMPLETED ✅**

This document outlined the user stories needed to complete the Python port of the C# JiraIssueConsole application. All features have been implemented and integrated into the CLI.

For implementation details, see `implementation-summary.md`.

## User Story 1: Offline JSON File Mode (--input)

**As a** data analyst  
**I want to** analyze pre-exported Jira issue data from a JSON file  
**So that** I can perform analysis without needing live Jira API access

### Acceptance Criteria
- CLI accepts `--input <JSON_FILE>` argument
- When `--input` is provided, the tool loads issues from the JSON file instead of calling the Jira API
- The JSON file format matches Jira REST API export format (see README.md for structure)
- File permissions are validated for security (warnings for group/world readable files)
- All export modes (--csv, --cfd, --status-timing, --transitions) work with JSON input
- Error handling for missing files, malformed JSON, and invalid formats

### Implementation Notes
- Use `json_input.load_issues_from_json()` which already exists
- Issues loaded from JSON need to be transformed to match the format expected by export functions
- Integration with workflow config (--workflow flag) should work with JSON input

### Testing
- Unit tests already exist in `tests/unit/test_json_input.py` for the loader
- Acceptance test exists in `tests/acceptance/test_offline_input.py`
- Verify all export modes work with JSON input

---

## User Story 2: Workflow Status Mapping (--workflow)

**As a** team lead with custom Jira workflows  
**I want to** normalize different status names to standard workflow states  
**So that** I can compare metrics across teams with different status configurations

### Acceptance Criteria
- CLI accepts `--workflow <WORKFLOW_FILE>` argument
- When `--workflow` is provided, status names are normalized according to the mapping file
- The workflow file format is parsed correctly (see workflow_config.py for format)
- Normalized statuses are used in all export modes
- Works with both API mode and offline JSON input mode

### Implementation Notes
- Use `workflow_config.load_workflow_config()` which already exists
- Pass the WorkflowConfig to export functions that support it:
  - export_cycle_time_rows() 
  - export_status_timing_rows()
  - export_transitions_rows()
  - calculate_cfd_data()
- Some functions already accept workflow parameter but it's not wired from CLI

### Testing
- Unit tests exist for workflow config parsing
- Need to test CLI integration with workflow config across all export modes
- Test with sample workflow.txt file

---

## User Story 3: Status Timing Export (--status-timing)

**As a** process improvement analyst  
**I want to** export the time each issue spent in each workflow status  
**So that** I can identify bottlenecks in our development process

### Acceptance Criteria
- CLI accepts `--status-timing <CSV_FILE>` argument
- Exports CSV with columns: key, [status1_days], [status2_days], etc.
- One row per issue showing days spent in each status
- Supports --workflow flag for status normalization
- Supports --business-days flag for business day calculations (Story 5)
- Works with both API mode and offline JSON input

### Implementation Notes
- Use `issue_timing.export_status_timing_rows()` which already exists
- Export to CSV using csv module
- Match the C# "_IssueTimes" export format

### Testing
- Unit tests exist for export_status_timing_rows()
- Add acceptance test for CLI integration
- Verify CSV format matches expected output

---

## User Story 4: Status Transitions Export (--transitions)

**As a** workflow analyst  
**I want to** export all status transitions for issues  
**So that** I can analyze how issues flow through our workflow

### Acceptance Criteria
- CLI accepts `--transitions <CSV_FILE>` argument
- Exports CSV with columns: key, from_status, to_status, date
- One row per transition event
- Supports --workflow flag for status normalization
- Works with both API mode and offline JSON input

### Implementation Notes
- Use `issue_timing.export_transitions_rows()` which already exists
- Export to CSV using csv module
- Match the C# "_Transitions" export format

### Testing
- Unit tests exist for export_transitions_rows()
- Add acceptance test for CLI integration
- Verify CSV format and date formatting

---

## User Story 5: Business Days Calculation (--business-days)

**As a** team manager  
**I want to** calculate cycle times using only business days  
**So that** I can exclude weekends and holidays from my metrics

### Acceptance Criteria
- CLI accepts `--business-days` flag
- When enabled, all time calculations use business days instead of calendar days
- Weekends (Saturday, Sunday) are excluded
- Works with all export modes (--csv, --cfd, --status-timing)
- Can be combined with --workflow flag

### Implementation Notes
- Add `--business-days` argument to CLI parser
- Pass `use_business_days=True` to functions that support it:
  - export_cycle_time_rows()
  - export_status_timing_rows()
- The business_days.compute_business_days() function already exists
- Holiday support exists but may need configuration mechanism

### Testing
- Unit tests exist in test_business_days.py and test_cycletime_business_days.py
- Add CLI integration tests for business days mode
- Verify calculations exclude weekends

---

## Implementation Order

The stories should be implemented in this order to build incrementally:

1. **Story 1 (--input)**: Foundation for offline mode, needed for other features
2. **Story 2 (--workflow)**: Status mapping needed by Stories 3 and 4
3. **Story 5 (--business-days)**: Calculation mode needed by Story 3
4. **Story 3 (--status-timing)**: Depends on Stories 2 and 5
5. **Story 4 (--transitions)**: Depends on Story 2

## C# Reference

The C# implementation in Program.cs shows the expected behavior:
- Takes 3 arguments: JsonFilename, ExportFilename, WorkflowFileName
- Exports 3 files: _IssueTimes, _Transitions, _CFD
- All features work together in a single execution

The Python implementation is more flexible with individual flags for each export mode.

---

## ✅ IMPLEMENTATION COMPLETE

All 5 user stories have been successfully implemented:

1. ✅ **Story 1 (--input)**: Offline JSON file mode
2. ✅ **Story 2 (--workflow)**: Workflow status mapping
3. ✅ **Story 3 (--status-timing)**: Status timing export
4. ✅ **Story 4 (--transitions)**: Status transitions export
5. ✅ **Story 5 (--business-days)**: Business days calculation

The Python port now has full CLI feature parity with the C# version.

See `implementation-summary.md` for detailed information about the implementation.
