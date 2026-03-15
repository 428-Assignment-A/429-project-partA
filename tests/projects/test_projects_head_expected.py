"""
test_projects_head_expected.py - Tests for documented behavior of HEAD /projects

Documented behavior:
  - "headers for all the instances of project"
  - Expected: 200 OK

Concern:
  - Wording suggests returning headers describing projects, but HEAD only returns HTTP headers.
  - If docs intended metadata, it should be in headers (e.g., Content-Length) or via GET.

Tests:
1. Returns 200
2. Must not return a response body (HEAD semantics)
3. Must include headers (at least one standard header)
"""

import pytest


class TestProjectsHeadExpected:

    @pytest.mark.capability
    def test_head_projects_returns_200(self, api):
        """Documented: HEAD /projects returns 200."""
        resp = api.head("/projects")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_head_projects_no_body(self, api):
        """HEAD should not return a response body."""
        resp = api.head("/projects")
        assert resp.text.strip() == ""

    @pytest.mark.capability
    def test_head_projects_returns_headers(self, api):
        """HEAD should return HTTP headers."""
        resp = api.head("/projects")
        assert len(resp.headers.keys()) > 0
