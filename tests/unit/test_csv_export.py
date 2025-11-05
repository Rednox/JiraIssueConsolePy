from jira_issue_console.core.csv_export import export_cycle_time_csv

def test_export_cycle_time_csv_basic():
    rows = [
        {"id": "1", "key": "TEST-1", "created": "2025-11-01T10:00:00.000+0000", "resolved": "2025-11-04T16:00:00.000+0000", "cycle_time_days": 2.0},
        {"id": "2", "key": "TEST-2", "created": "2025-12-24T09:00:00.000+0000", "resolved": "2025-12-27T17:00:00.000+0000", "cycle_time_days": 1.0},
    ]
    csv_str = export_cycle_time_csv(rows)
    lines = csv_str.strip().splitlines()
    assert lines[0] == "id,key,created,resolved,cycle_time_days"
    assert lines[1].startswith("1,TEST-1,2025-11-01T10:00:00.000+0000,2025-11-04T16:00:00.000+0000,2.0")
    assert lines[2].startswith("2,TEST-2,2025-12-24T09:00:00.000+0000,2025-12-27T17:00:00.000+0000,1.0")

def test_export_cycle_time_csv_empty():
    csv_str = export_cycle_time_csv([])
    assert csv_str.strip() == "id,key,created,resolved,cycle_time_days"