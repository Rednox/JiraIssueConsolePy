"""Basic smoke tests for the scaffold.

This test uses asyncio.run to exercise the async `list_issues` function so it works
in both local and CI environments without introducing pytest-asyncio here.
"""

import unittest
import asyncio
import os
import respx


class SmokeTest(unittest.TestCase):
    @respx.mock
    def test_import_and_list(self):
        # Import the package and call list_issues with an arbitrary project key.
        from jira_issue_console.core import issues

        # Mock the Jira API endpoint
        base_url = os.environ.get("JIRA_BASE_URL", "https://jira.example.com")
        url = f"{base_url}/rest/api/2/search"
        respx.get(url).respond(
            200, json={"issues": [{"id": "1", "key": "TEST-1", "fields": {}}]}
        )

        res = asyncio.run(issues.list_issues("PROJ"))
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
