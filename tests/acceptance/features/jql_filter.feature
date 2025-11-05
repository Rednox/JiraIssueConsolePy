Feature: Filter issues using JQL
  As a user
  I want to filter issues using JQL
  So that I can find specific issues matching criteria

  Scenario: Filter issues by priority
    Given a project "TEST" with high priority issues
    When I run the CLI with project "TEST" and JQL filter "priority = High"
    Then I should only see high priority issues in the output