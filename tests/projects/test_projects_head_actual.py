"""
test_projects_head_actual.py - Observed behavior for HEAD /projects

Observed behavior (Postman):
  - Status: 200
  - Body: empty (expected for HEAD)
  - Headers visible in Postman 'Headers' tab (e.g., Content-Type, Server, Date)

Tests:
1. HEAD returns 200
2. HEAD response body is empty
3. HEAD returns at least one useful header (Content-Type or Date)
"""

import pytest


class TestProjectsHeadActual:

    @pytest.mark.capability
    def test_head_projects_returns_200(self, api):
        """Verify HEAD /projects returns 200."""
        resp = api.head("/projects")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_head_projects_body_empty(self, api):
        """Verify HEAD /projects has an empty body."""
        resp = api.head("/projects")
        assert resp.text.strip() == ""

    @pytest.mark.capability
    def test_head_projects_has_useful_headers(self, api):
        """Verify HEAD /projects includes at least one common header."""
        resp = api.head("/projects")
        assert ("Date" in resp.headers) or ("Content-Type" in resp.headers) or ("Server" in resp.headers)
