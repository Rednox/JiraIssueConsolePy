Feature: Process offline JSON files
  As a user
  I want to analyze pre-exported Jira data
  So that I can work offline or with historical snapshots

  Scenario: Export cycle times from JSON file
    Given I have a Jira JSON export file
    When I run "jira_issue_console PROJ --input example.json --csv cycle_times.csv"
    Then a CSV file "cycle_times.csv" is created
    And it contains cycle times for the exported issues

  Scenario: Generate CFD from JSON file
    Given I have a Jira JSON export file
    When I run "jira_issue_console PROJ --input example.json --cfd cfd.csv"
    Then a CSV file "cfd.csv" is created
    And it shows daily status counts

  Scenario: Analyze transitions from JSON with workflow mapping
    Given I have a Jira JSON export file
    And I have a workflow file:
      """
      In Review -> In Progress
      Testing -> In Progress
      """
    When I run "jira_issue_console PROJ --input example.json --workflow workflow.txt --transitions transitions.csv"
    Then a CSV file "transitions.csv" is created
    And status transitions use mapped names