"""
test_projects_delete.py - Tests for DELETE /projects endpoint

Documented behavior:
  - Method not allowed
  - Expected: 405

Tests:
1. Return code (405)
2. No side effects
3. Data survives failed DELETE
4. DELETE with query params rejected
"""

import pytest


class TestProjectsDelete:

    # 1. Capability: Method not allowed
    @pytest.mark.error
    def test_delete_projects_returns_405(self, api):
        """Verify DELETE /projects returns 405 Method Not Allowed."""
        resp = api.delete("/projects")
        assert resp.status_code == 405

    # 2. Side effects: No data modification
    @pytest.mark.capability
    def test_delete_projects_no_side_effects(self, api):
        """Verify DELETE /projects does not delete existing projects."""
        api.post("/projects", json={"title": "PersistentProject"})
        before = api.get("/projects").json()

        api.delete("/projects")

        after = api.get("/projects").json()
        assert before == after

    # 3. Safety: Data survives failed DELETE
    @pytest.mark.capability
    def test_delete_projects_data_survives(self, api):
        """Ensure failed DELETE does not clear project data."""
        api.post("/projects", json={"title": "SurvivorProject"})

        api.delete("/projects")

        resp = api.get("/projects")
        titles = [p["title"] for p in resp.json().get("projects", [])]
        assert "SurvivorProject" in titles

    # 4. Error case: DELETE with query parameters
    @pytest.mark.error
    def test_delete_projects_with_params_rejected(self, api):
        """Verify DELETE /projects with query params is still rejected."""
        resp = api.delete("/projects?title=Anything")
        assert resp.status_code == 405
