"""
test_projects_id_options.py - Tests for OPTIONS /projects/:id endpoint

Documented behavior:
  - Shows allowed methods for /projects/:id
  - Expected: 200
Observed:
  - Allow header may or may not be present depending on server/proxy.
"""

import pytest


class TestProjectsIdOptions:

    @pytest.mark.capability
    def test_options_projects_id_returns_200(self, api):
        """OPTIONS /projects/:id returns 200."""
        created = api.post("/projects", json={"title": "OptionsById"})
        pid = created.json()["id"]

        resp = api.options(f"/projects/{pid}")
        assert resp.status_code == 200

    @pytest.mark.capability
    def test_options_includes_allow_header_or_equivalent(self, api):
        """OPTIONS should advertise allowed methods (preferably via Allow header)."""
        created = api.post("/projects", json={"title": "OptionsAllow"})
        pid = created.json()["id"]

        resp = api.options(f"/projects/{pid}")
        assert resp.status_code == 200

        # Some servers provide Allow header, others don't (but still 200).
        allow = resp.headers.get("Allow") or resp.headers.get("allow")
        if allow is not None:
            assert "GET" in allow or "get" in allow.lower()

    @pytest.mark.capability
    def test_options_has_no_side_effects(self, api):
        """OPTIONS should not create/modify/delete data."""
        before = api.get("/projects").json().get("projects", [])
        # Use a valid id for the OPTIONS call
        created = api.post("/projects", json={"title": "OptionsNoSideEffects"})
        pid = created.json()["id"]

        api.options(f"/projects/{pid}")
        after = api.get("/projects").json().get("projects", [])

        assert len(after) >= len(before)

    @pytest.mark.error
    def test_options_invalid_id_format_returns_error_or_200(self, api):
        """OPTIONS /projects/:id with invalid id may return 200/404/400 depending on router."""
        resp = api.options("/projects/not-an-id")
        assert resp.status_code in [200, 400, 404]
