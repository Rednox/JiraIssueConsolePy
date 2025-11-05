Feature: Export workflow metrics
  As a team lead
  I want to analyze our workflow metrics
  So that I can identify bottlenecks and improve processes

  Background:
    Given I have Jira credentials configured
    And a project with issues exists

  Scenario: Generate Cumulative Flow Diagram data
    When I run "jira_issue_console PROJ --cfd cfd.csv"
    Then a CSV file "cfd.csv" is created
    And it has header "Date,Open,In Progress,Done"
    And each row has counts per status

  Scenario: Export time spent in each status
    When I run "jira_issue_console PROJ --status-timing status_times.csv"
    Then a CSV file "status_times.csv" is created
    And it has header "key,Open,In Progress,Done"
    And each issue has time in each status

  Scenario: Export status transition history
    When I run "jira_issue_console PROJ --transitions transitions.csv"
    Then a CSV file "transitions.csv" is created
    And it has header "key,from_status,to_status,date"
    And each transition shows status change date

  Scenario: Use workflow status mapping
    Given I have a workflow file:
      """
      In Review -> In Progress
      Testing -> In Progress
      Ready for QA -> In Progress
      """
    When I run "jira_issue_console PROJ --workflow workflow.txt --transitions transitions.csv"
    Then a CSV file "transitions.csv" is created
    And status "In Review" is mapped to "In Progress"
    And status "Testing" is mapped to "In Progress"