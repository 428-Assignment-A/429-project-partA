"""
test_projects_options_actual.py - Observed behavior for OPTIONS /projects

Observed behavior (Postman):
  - Status: 200
  - Body: empty
  - Response headers include Allow: OPTIONS, GET, HEAD, POST

Tests:
1. OPTIONS returns 200
2. Allow header exists
3. Allow contains expected methods
4. Response body is empty
"""

import pytest


class TestProjectsOptionsActual:

    @pytest.mark.capability
    def test_options_projects_returns_200(self, api):
        """Verify OPTIONS /projects returns 200."""
        resp = api.options("/projects")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_options_projects_has_allow_header(self, api):
        """Verify OPTIONS /projects provides an Allow header."""
        resp = api.options("/projects")
        assert "Allow" in resp.headers

    @pytest.mark.capability
    def test_options_projects_allow_lists_methods(self, api):
        """Verify Allow header includes OPTIONS, GET, HEAD, POST."""
        resp = api.options("/projects")
        allow = resp.headers.get("Allow", "")
        for m in ["OPTIONS", "GET", "HEAD", "POST"]:
            assert m in allow

    @pytest.mark.capability
    def test_options_projects_empty_body(self, api):
        """Verify OPTIONS /projects response body is empty."""
        resp = api.options("/projects")
        assert resp.text.strip() == ""
