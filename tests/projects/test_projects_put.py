"""
test_projects_put.py - Tests for PUT /projects endpoint

Documented behavior:
  - Often "method not allowed" on collection endpoints
  - Expected: 405 (based on your sheet for /projects PUT)

Tests:
1. PUT /projects returns 405
2. No side effects (data unchanged)
3. PUT with body still rejected
"""

import pytest


class TestProjectsPut:

    @pytest.mark.error
    def test_put_projects_returns_405(self, api):
        """Verify PUT /projects returns 405 Method Not Allowed."""
        resp = api.put("/projects", json={"title": "ShouldNotWork"})
        assert resp.status_code == 405

    @pytest.mark.capability
    def test_put_projects_no_side_effects(self, api):
        """Verify failed PUT /projects does not modify existing data."""
        api.post("/projects", json={"title": "StableProject", "completed": False, "active": True})
        before = api.get("/projects").json().get("projects", [])

        api.put("/projects", json={"title": "Nope"})
        after = api.get("/projects").json().get("projects", [])

        assert before == after

    @pytest.mark.error
    def test_put_projects_with_query_params_rejected(self, api):
        """Verify PUT /projects rejected even with query params."""
        resp = api.put("/projects?title=X", json={"title": "X"})
        assert resp.status_code == 405
