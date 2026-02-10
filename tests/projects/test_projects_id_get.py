"""
test_projects_id_get.py - Tests for GET /projects/:id endpoint

Documented behavior:
  - Returns a specific project by id
  - Expected: 200 (project exists), 404 (not found)

Tests:
1. GET existing project returns 200
2. Response contains correct id
3. Response contains correct fields
4. GET deleted project returns 404
5. GET non-existent id returns 404
6. GET invalid id format returns 400 or 404
7. Response Content-Type is JSON
"""

import pytest


class TestProjectsIdGet:

    @pytest.mark.capability
    def test_get_existing_project_returns_200(self, api):
        """Verify GET /projects/:id returns 200 for an existing project."""
        created = api.post("/projects", json={"title": "GetById", "completed": False, "active": True})
        pid = created.json()["id"]

        resp = api.get(f"/projects/{pid}")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_get_project_contains_correct_id(self, api):
        """Verify returned project has the requested id."""
        created = api.post("/projects", json={"title": "CorrectId"})
        pid = created.json()["id"]

        resp = api.get(f"/projects/{pid}")
        assert resp.status_code == 200

        body = resp.json()
        # Some versions wrap: {"projects":[{...}]}, others return {...}
        if "projects" in body:
            assert str(body["projects"][0]["id"]) == str(pid)
        else:
            assert str(body["id"]) == str(pid)

    @pytest.mark.capability
    def test_get_project_contains_expected_fields(self, api):
        """Verify basic project fields exist in response."""
        created = api.post("/projects", json={
            "title": "FieldCheck",
            "completed": False,
            "active": True,
            "description": "desc"
        })
        pid = created.json()["id"]

        resp = api.get(f"/projects/{pid}")
        assert resp.status_code == 200
        body = resp.json()

        proj = body["projects"][0] if "projects" in body else body
        for key in ["id", "title", "completed", "active"]:
            assert key in proj

    @pytest.mark.capability
    def test_get_deleted_project_returns_404(self, api):
        """After deletion, GET /projects/:id should return 404."""
        created = api.post("/projects", json={"title": "DeleteThenGet"})
        pid = created.json()["id"]

        api.delete(f"/projects/{pid}")
        resp = api.get(f"/projects/{pid}")
        assert resp.status_code == 404

    @pytest.mark.error
    def test_get_nonexistent_project_returns_404(self, api):
        """Verify GET /projects/:id returns 404 for unknown id."""
        resp = api.get("/projects/999999")
        assert resp.status_code == 404

    @pytest.mark.error
    def test_get_invalid_id_format_returns_error(self, api):
        """Verify GET /projects/:id rejects invalid id formats."""
        resp = api.get("/projects/not-an-id")
        assert resp.status_code in [400, 404]

    @pytest.mark.capability
    def test_get_project_content_type_json(self, api):
        """Verify response is JSON when requesting JSON."""
        created = api.post("/projects", json={"title": "JsonHeader"})
        pid = created.json()["id"]

        resp = api.get(f"/projects/{pid}", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
