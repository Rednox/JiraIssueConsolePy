Feature: Export cycle times to CSV
  As a user
  I want to export issue cycle times to CSV
  So that I can analyze the data in spreadsheet software

  Scenario: Export cycle times for a project
    Given a project "TEST" with 2 issues
    When I run the CLI with project "TEST" and CSV export to "cycle_times.csv"
    Then the CSV file should contain headers and 2 rows of cycle time data