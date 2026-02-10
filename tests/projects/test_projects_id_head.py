"""
test_projects_id_head.py - Tests for HEAD /projects/:id endpoint

Documented behavior:
  - Returns headers for a specific project by id
  - Expected: 200 (exists), 404 (not found)
Note: HEAD responses have no body by definition.
"""

import pytest


class TestProjectsIdHead:

    @pytest.mark.capability
    def test_head_existing_project_returns_200(self, api):
        """HEAD /projects/:id returns 200 for existing project."""
        created = api.post("/projects", json={"title": "HeadById", "completed": False, "active": True})
        pid = created.json()["id"]

        resp = api.head(f"/projects/{pid}")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_head_has_no_body(self, api):
        """HEAD should not return a response body."""
        created = api.post("/projects", json={"title": "HeadNoBody"})
        pid = created.json()["id"]

        resp = api.head(f"/projects/{pid}")
        assert resp.status_code == 200
        assert resp.text in ["", None]

    @pytest.mark.capability
    def test_head_includes_content_type_header(self, api):
        """HEAD should include Content-Type or basic response headers."""
        created = api.post("/projects", json={"title": "HeadHeaders"})
        pid = created.json()["id"]

        resp = api.head(f"/projects/{pid}")
        assert resp.status_code == 200
        assert "Content-Type" in resp.headers or "content-type" in {k.lower() for k in resp.headers.keys()}

    @pytest.mark.error
    def test_head_nonexistent_project_returns_404(self, api):
        """HEAD /projects/:id returns 404 when project does not exist."""
        resp = api.head("/projects/999999")
        assert resp.status_code == 404

    @pytest.mark.error
    def test_head_invalid_id_format_returns_error(self, api):
        """HEAD /projects/:id rejects invalid id formats."""
        resp = api.head("/projects/not-an-id")
        assert resp.status_code in [400, 404]
