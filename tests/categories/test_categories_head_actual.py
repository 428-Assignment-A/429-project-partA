"""
test_categories_head_actual.py - Actual behavior for HEAD /categories

Bug: HEAD /categories is documented as returning headers for all the instances
of category. The body in the response was empty when it should've returned all
the headers for the instances of category.

Observed: 200 OK with empty response.

Module 2 (Actual Behavior - PASSING):
  Tests what the API actually does. All tests PASS, documenting the bug.
"""

import pytest


class TestCategoriesHeadActual:

    # 1. Core Functionality: Returns 200 but empty response
    @pytest.mark.bug
    def test_head_categories_returns_empty_response(self, api):
        """Actual: HEAD /categories returns 200 OK but the response is empty."""
        api.post("/categories", json={"title": "Category A"})

        resp = api.head("/categories")
        assert resp.status_code == 200
        assert len(resp.content) == 0

    # 2. Return Code: 200 OK
    @pytest.mark.bug
    def test_head_categories_returns_200(self, api):
        """Actual: HEAD /categories returns 200 OK."""
        resp = api.head("/categories")
        assert resp.status_code == 200

    # 3. Observed: Missing Content-Length, uses chunked encoding
    @pytest.mark.bug
    def test_head_categories_missing_content_length(self, api):
        """Actual: Server uses Transfer-Encoding: chunked instead of Content-Length,
        so the response does not describe the size of the category data."""
        resp = api.head("/categories")
        assert resp.status_code == 200
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert resp.headers.get("Content-Length") is None

    # 4. Side Effects: HEAD does not modify data
    @pytest.mark.bug
    def test_head_categories_no_side_effects(self, api):
        """Actual: HEAD does not modify the categories collection."""
        api.post("/categories", json={"title": "Stable"})
        count_before = len(api.get("/categories").json()["categories"])

        api.head("/categories")

        count_after = len(api.get("/categories").json()["categories"])
        assert count_before == count_after

    # 5. Observed: Empty response regardless of Accept header
    @pytest.mark.bug
    def test_head_categories_empty_regardless_of_accept(self, api):
        """Actual: Response is empty regardless of Accept header value."""
        for accept in ["application/json", "application/xml"]:
            resp = api.head("/categories", headers={"Accept": accept})
            assert resp.status_code == 200
            assert len(resp.content) == 0
