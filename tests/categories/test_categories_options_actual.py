"""
test_categories_options_actual.py - Actual behavior for OPTIONS /categories

Bug: This endpoint was not documented in the official docs, but the swagger
json description indicates it should show all the options for the endpoints
for categories. The endpoint returns an empty response instead.

Module 2 (Actual Behavior - PASSING):
  Tests what the API actually does. All tests PASS, documenting the bug.
"""

import pytest


class TestCategoriesOptionsActual:

    # 1. Core Functionality: Returns 200 but with empty body
    @pytest.mark.bug
    def test_options_categories_returns_empty_body(self, api):
        """Actual: OPTIONS /categories returns 200 OK but the response body is empty."""
        resp = api.options("/categories")
        assert resp.status_code == 200
        assert len(resp.text.strip()) == 0

    # 2. Return Code: Verify 200 status
    @pytest.mark.bug
    def test_options_categories_returns_200(self, api):
        """Actual: OPTIONS /categories returns 200 OK."""
        resp = api.options("/categories")
        assert resp.status_code == 200

    # 3. Capability: Allow header is present
    @pytest.mark.bug
    def test_options_categories_has_allow_header(self, api):
        """Actual: The Allow header is present even though the body is empty."""
        resp = api.options("/categories")
        assert resp.status_code == 200
        allow = resp.headers.get("Allow", "")
        assert "GET" in allow
        assert "POST" in allow

    # 4. Side Effects: OPTIONS does not modify data
    @pytest.mark.bug
    def test_options_categories_no_side_effects(self, api):
        """Actual: OPTIONS does not modify the categories collection."""
        api.post("/categories", json={"title": "Stable"})
        initial_count = len(api.get("/categories").json()["categories"])

        api.options("/categories")

        final_count = len(api.get("/categories").json()["categories"])
        assert initial_count == final_count

    # 5. Format: No content type in response body
    @pytest.mark.bug
    def test_options_categories_empty_regardless_of_accept(self, api):
        """Actual: Body remains empty regardless of Accept header."""
        for accept in ["application/json", "application/xml"]:
            resp = api.options("/categories", headers={"Accept": accept})
            assert resp.status_code == 200
            assert len(resp.text.strip()) == 0
