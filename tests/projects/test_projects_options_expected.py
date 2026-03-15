"""
test_projects_options_expected.py - Tests for documented behavior of OPTIONS /projects

Documented behavior:
  - "show all Options for endpoint of projects"
  - Expected: 200 OK (empty response)

Concern:
  - Documentation implies body may describe options, but observed body is empty.

Tests:
1. Returns 200
2. Body should not be empty (expected doc usefulness) OR explicitly confirm mismatch
"""

import pytest


class TestProjectsOptionsExpected:

    @pytest.mark.capability
    def test_options_projects_returns_200(self, api):
        """Documented: OPTIONS /projects returns 200."""
        resp = api.options("/projects")
        assert resp.status_code == 200

    @pytest.mark.xfail(reason="Docs imply options info; observed body is empty.")
    def test_options_projects_body_describes_options(self, api):
        """
        Expected (from docs wording): body provides some information about allowed methods.
        Observed: empty body in Postman.
        """
        resp = api.options("/projects")
        assert resp.text.strip() != ""
