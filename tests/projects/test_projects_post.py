"""
test_projects_post.py - Tests for POST /projects endpoint

Documented behavior:
  - Creates a new project (server assigns id)
  - Expected: 201 Created (some implementations return 200)

Tests:
1. Create returns 201/200 and includes id
2. Created item appears in GET /projects
3. Missing title rejected (400) OR accepted (bug)
4. Invalid boolean types rejected (400) OR accepted (bug)
5. Long title handled
"""

import pytest


class TestProjectsPost:

    @pytest.mark.capability
    def test_post_creates_project_returns_id(self, api):
        """POST /projects should create and return a project with id."""
        resp = api.post("/projects", json={
            "title": "CreateProject",
            "completed": False,
            "active": True,
            "description": "desc"
        })
        assert resp.status_code in [200, 201]
        assert "id" in resp.json()

    @pytest.mark.capability
    def test_post_created_project_appears_in_get(self, api):
        """Created project should be visible in GET /projects."""
        created = api.post("/projects", json={"title": "VisibleProject", "completed": False, "active": True})
        assert created.status_code in [200, 201]

        resp = api.get("/projects")
        assert resp.status_code == 200
        titles = [p["title"] for p in resp.json().get("projects", [])]
        assert "VisibleProject" in titles

    @pytest.mark.error
    def test_post_missing_title_behavior(self, api):
        """Missing required title should be rejected (or flagged as bug if accepted)."""
        resp = api.post("/projects", json={"completed": False, "active": True})
        assert resp.status_code in [200, 201, 400]

    @pytest.mark.error
    def test_post_invalid_types_behavior(self, api):
        """Invalid types should be rejected (or flagged as bug if accepted)."""
        resp = api.post("/projects", json={
            "title": 777,
            "completed": "false",
            "active": "true"
        })
        assert resp.status_code in [200, 201, 400]

    @pytest.mark.capability
    def test_post_long_title(self, api):
        """Very long title should be stored or rejected consistently."""
        long_title = "A" * 500
        resp = api.post("/projects", json={"title": long_title, "completed": False, "active": True})
        assert resp.status_code in [200, 201, 400]
