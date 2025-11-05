Feature: Export Cumulative Flow Diagram (CFD) data
  As a user
  I want to export CFD data to CSV
  So that I can analyze flow metrics and create CFD visualizations

  Scenario: Export CFD data for a project
    Given a project "TEST" with issues and transitions
    When I run the CLI with project "TEST" and CFD export to "cfd.csv"
    Then the CFD CSV file should contain status counts per date