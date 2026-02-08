"""
test_categories_id_options_actual.py - Actual behavior for OPTIONS /categories/:id

Bug: This endpoint was not documented in the official docs, but the swagger
json description indicates it should show all the options for the endpoints
for categories of a specific ID. The endpoint returns an empty response instead.

Module 2 (Actual Behavior - PASSING):
  Tests what the API actually does. All tests PASS, documenting the bug.
"""

import pytest


class TestCategoriesIdOptionsActual:

    # 1. Core Functionality: Returns 200 but with empty body
    @pytest.mark.bug
    def test_options_id_returns_empty_body(self, api):
        """Actual: OPTIONS /categories/:id returns 200 OK but the response body is empty."""
        cat_id = api.post("/categories", json={"title": "Empty Body"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert len(resp.text.strip()) == 0

    # 2. Return Code: Verify 200 status
    @pytest.mark.bug
    def test_options_id_returns_200(self, api):
        """Actual: OPTIONS /categories/:id returns 200 OK."""
        cat_id = api.post("/categories", json={"title": "Status Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        assert resp.status_code == 200

    # 3. Capability: Allow header is present despite empty body
    @pytest.mark.bug
    def test_options_id_has_allow_header(self, api):
        """Actual: The Allow header is present listing methods, even though body is empty."""
        cat_id = api.post("/categories", json={"title": "Allow Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        assert resp.status_code == 200
        allow = resp.headers.get("Allow", "")
        for method in ["GET", "PUT", "POST", "DELETE", "OPTIONS"]:
            assert method in allow

    # 4. Side Effects: OPTIONS does not modify data
    @pytest.mark.bug
    def test_options_id_no_side_effects(self, api):
        """Actual: OPTIONS does not modify the targeted category."""
        cat_id = api.post("/categories", json={"title": "Safe Data"}).json()["id"]

        api.options(f"/categories/{cat_id}")

        check = api.get(f"/categories/{cat_id}")
        assert check.json()["categories"][0]["title"] == "Safe Data"

    # 5. Format: Body remains empty regardless of Accept header
    @pytest.mark.bug
    def test_options_id_empty_regardless_of_accept(self, api):
        """Actual: Body remains empty regardless of Accept header."""
        cat_id = api.post("/categories", json={"title": "Accept Test"}).json()["id"]

        for accept in ["application/json", "application/xml"]:
            resp = api.options(f"/categories/{cat_id}", headers={"Accept": accept})
            assert resp.status_code == 200
            assert len(resp.text.strip()) == 0
