"""
test_projects_id_delete.py - Tests for DELETE /projects/:id endpoint

Documented behavior:
  - Deletes a specific project by id
  - Expected: 200

Tests:
1. Delete existing project (200)
2. Confirm deleted project is gone (404)
3. Delete non-existent id (404)
4. Delete invalid id format (400 or 404)
5. Delete twice (second should fail)
6. Delete does not remove other projects
"""

import pytest


class TestProjectsIdDelete:

    @pytest.mark.capability
    def test_delete_existing_project_returns_200(self, api):
        """Verify DELETE /projects/:id deletes an existing project."""
        created = api.post("/projects", json={"title": "ToDelete"})
        pid = created.json()["id"]

        resp = api.delete(f"/projects/{pid}")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_delete_project_then_get_returns_404(self, api):
        """After DELETE, GET /projects/:id should return 404."""
        created = api.post("/projects", json={"title": "DeleteThenMissing"})
        pid = created.json()["id"]

        api.delete(f"/projects/{pid}")
        resp = api.get(f"/projects/{pid}")
        assert resp.status_code == 404

    @pytest.mark.error
    def test_delete_nonexistent_project_returns_404(self, api):
        """Verify DELETE /projects/:id returns 404 for unknown id."""
        resp = api.delete("/projects/999999")
        assert resp.status_code == 404

    @pytest.mark.error
    def test_delete_invalid_id_format_returns_error(self, api):
        """Verify DELETE /projects/:id rejects invalid id formats."""
        resp = api.delete("/projects/not-an-id")
        assert resp.status_code in [400, 404]

    @pytest.mark.error
    def test_delete_same_project_twice_second_fails(self, api):
        """Second DELETE of same id should fail (404)."""
        created = api.post("/projects", json={"title": "DeleteTwice"})
        pid = created.json()["id"]

        first = api.delete(f"/projects/{pid}")
        assert first.status_code == 200

        second = api.delete(f"/projects/{pid}")
        assert second.status_code == 404

    @pytest.mark.capability
    def test_delete_one_project_does_not_delete_others(self, api):
        """Deleting one project should not remove other projects."""
        p1 = api.post("/projects", json={"title": "KeepMe"}).json()["id"]
        p2 = api.post("/projects", json={"title": "RemoveMe"}).json()["id"]

        api.delete(f"/projects/{p2}")

        resp = api.get(f"/projects/{p1}")
        assert resp.status_code == 200
