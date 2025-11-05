"""Basic smoke tests for the scaffold.

This test uses asyncio.run to exercise the async `list_issues` function so it works
in both local and CI environments without introducing pytest-asyncio here.
"""
import unittest
import asyncio


class SmokeTest(unittest.TestCase):
    def test_import_and_list(self):
        # Import the package and call list_issues with an arbitrary project key.
        from jira_issue_console.core import issues

        res = asyncio.run(issues.list_issues("PROJ"))
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
