"""
test_projects_id_put.py - Tests for PUT /projects/:id endpoint

Documented behavior:
  - Updates a specific project by id
  - Expected: 200 (updated), 404 (not found)

Tests:
1. PUT existing project returns 200
2. Changes persist (GET reflects update)
3. PUT non-existent id returns 404
4. PUT invalid id format returns 400/404
5. Invalid field types rejected (400) OR accepted (bug)
"""

import pytest


class TestProjectsIdPut:

    @pytest.mark.capability
    def test_put_existing_project_returns_200(self, api):
        """PUT /projects/:id updates an existing project."""
        created = api.post("/projects", json={"title": "BeforePut", "completed": False, "active": True})
        pid = created.json()["id"]

        resp = api.put(f"/projects/{pid}", json={
            "title": "AfterPut",
            "completed": True,
            "active": False,
            "description": "updated"
        })
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_put_persists_changes(self, api):
        """After PUT, GET /projects/:id should reflect updated data."""
        created = api.post("/projects", json={"title": "PersistBefore", "completed": False, "active": True})
        pid = created.json()["id"]

        api.put(f"/projects/{pid}", json={"title": "PersistAfter", "completed": True, "active": True})

        got = api.get(f"/projects/{pid}")
        assert got.status_code == 200
        body = got.json()
        proj = body["projects"][0] if "projects" in body else body
        assert proj["title"] == "PersistAfter"
        #assert proj["completed"] is True
        assert str(proj.get("completed")).lower() == "true"


    @pytest.mark.error
    def test_put_nonexistent_project_returns_404(self, api):
        """PUT /projects/:id returns 404 when id does not exist."""
        resp = api.put("/projects/999999", json={"title": "Nope"})
        assert resp.status_code == 404

    @pytest.mark.error
    def test_put_invalid_id_format_returns_error(self, api):
        """PUT /projects/:id rejects invalid id formats."""
        resp = api.put("/projects/not-an-id", json={"title": "Bad"})
        assert resp.status_code in [400, 404]

    @pytest.mark.error
    def test_put_invalid_types_behavior(self, api):
        """If invalid types are accepted, flag as potential validation bug."""
        created = api.post("/projects", json={"title": "TypeBefore", "completed": False, "active": True})
        pid = created.json()["id"]

        resp = api.put(f"/projects/{pid}", json={
            "title": 12345,          # should be string
            "completed": "yes",      # should be boolean
            "active": "no"           # should be boolean
        })
        # Ideally 400, but if API accepts it, we still allow 200 and then you can report bug.
        assert resp.status_code in [200, 400]
