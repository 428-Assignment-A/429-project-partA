"""
test_projects_get.py - Tests for GET /projects endpoint

Documented behavior:
  - Returns all instances of project
  - Expected: 200

Tests:
1. Core functionality
2. JSON/XML format
3. Return codes
4. Side effects
5. Query parameter filtering
"""

import pytest


class TestProjectsGet:

    # 1. Capability: Return all instances
    @pytest.mark.capability
    def test_get_all_projects_returns_list(self, api):
        """Confirm GET /projects returns the list of all projects."""
        resp = api.get("/projects")
        assert resp.status_code == 200
        assert "projects" in resp.json()
        assert isinstance(resp.json()["projects"], list)

    # 2. Capability: Verify returned data matches created data
    @pytest.mark.capability
    def test_get_projects_contains_created_item(self, api):
        """ Verify that a project created via POST /projects appears in the GET /projects response."""
        createProject = api.post("/projects", json={
            "title": "TestProject1", "completed": False, "active": True, "description": "Test description1"
            })
        assert createProject.status_code in [200, 201]
        resp = api.get("/projects")
        titles = [p.get("title") for p in resp.json()["projects"]]
        assert "TestProject1" in titles

    # 3. Capability: Long title support
    @pytest.mark.capability
    def test_get_projects_contains_long_title(self, api):
        """Verify the API can store and return an extremely long title."""
        long_title = "A" * 500
        api.post("/projects", json={"title": long_title, "completed": False, "active": True})

        resp = api.get("/projects")
        titles = [p["title"] for p in resp.json()["projects"]]
        assert long_title in titles

    # 4. Capability: Special characters support
    @pytest.mark.capability
    def test_get_projects_contains_special_chars(self, api):
        """Verify the API stores and returns XSS scripts and special characters."""
        special = "<script>alert('xss')</script> é ñ 中文"
        api.post("/projects", json={"title": special, "completed": False, "active": True})

        resp = api.get("/projects")
        titles = [p.get("title") for p in resp.json()["projects"]]
        assert special in titles

    # 5. Command Line Query: Filter by description
    @pytest.mark.capability
    def test_get_projects_filter_by_description(self, api):
        """Verify filtering via query parameters: /projects?description=..."""
        unique_desc = "UniqueProjectDesc"
        api.post("/projects", json={"title": "Test", "description": unique_desc, "completed": False, "active": True})

        resp = api.get(f"/projects?description={unique_desc}")
        assert resp.status_code == 200
        for proj in resp.json()["projects"]:
            assert proj["description"] == unique_desc

    # 6. Format: JSON Response
    @pytest.mark.capability
    def test_get_projects_json_format(self, api):
        """Verify JSON response structure and headers."""
        resp = api.get("/projects", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

    # 7. Side Effects: GET is idempotent
    @pytest.mark.capability
    def test_get_projects_no_side_effects(self, api):
        """Verify that GET /projects does not modify any data."""
        before = api.get("/projects").json().get("projects", [])
        api.get("/projects")
        api.get("/projects")
        after = api.get("/projects").json().get("projects", [])
        assert len(before) == len(after)

    # 8. Error Case: Filter returns empty results
    @pytest.mark.error
    def test_get_projects_filter_no_results(self, api):
        """Verify filtering for a non-existent item returns an empty list."""
        resp = api.get("/projects?title=ThisTitleShouldNotExist12345")
        assert resp.status_code == 200
        assert len(resp.json()["projects"]) == 0

    # 9. Error Case: Malformed Accept header
    @pytest.mark.error
    def test_get_projects_malformed_accept_header(self, api):
        """Verify behavior when Accept header is nonsense."""
        resp = api.get("/projects", headers={"Accept": "not-a-real-format"})
        assert resp.status_code in [200, 406]
