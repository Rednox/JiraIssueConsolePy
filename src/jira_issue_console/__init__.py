"""jira_issue_console package

Lightweight package initializer for the JiraIssueConsolePy project.
"""
__version__ = "0.1.0-alpha"
__all__ = ["cli", "core", "jira_client", "models"]

# Compatibility shim for respx: some tests expect the mocked router fixture
# to expose `Response` as an attribute (respx_mock.Response). If respx is
# installed, ensure MockRouter has a Response attribute referencing the
# top-level Response class to keep tests compatible across respx versions.
try:
	import respx
	from httpx import Response
	if hasattr(respx, "router"):
		setattr(respx.router.MockRouter, "Response", Response)
except (ImportError, AttributeError):
	# Not critical if respx is unavailable in the environment or structure differs
	pass
