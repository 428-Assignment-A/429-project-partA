"""
test_categories_id_head_actual.py - Actual behavior for HEAD /categories/:id

Bug: HEAD /categories/:id is documented as returning headers for a specific
instance of category using an id. The endpoint should've returned all the
headers for the instances of category of a specific ID, but instead returned
200 OK with an empty response.

Observed: 200 OK with empty response.

Module 2 (Actual Behavior - PASSING):
  Tests what the API actually does. All tests PASS, documenting the bug.
"""

import pytest


class TestCategoriesIdHeadActual:

    # 1. Core Functionality: Returns 200 but empty response
    @pytest.mark.bug
    def test_head_id_returns_empty_response(self, api):
        """Actual: HEAD /categories/:id returns 200 OK but the response is empty."""
        cat_id = api.post("/categories", json={"title": "Head Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert len(resp.content) == 0

    # 2. Return Code: 200 OK
    @pytest.mark.bug
    def test_head_id_returns_200(self, api):
        """Actual: HEAD /categories/:id returns 200 OK."""
        cat_id = api.post("/categories", json={"title": "Status Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}")
        assert resp.status_code == 200

    # 3. Observed: Missing Content-Length, uses chunked encoding
    @pytest.mark.bug
    def test_head_id_missing_content_length(self, api):
        """Actual: Server uses Transfer-Encoding: chunked instead of Content-Length,
        so the response does not describe the size of the category data."""
        cat_id = api.post("/categories", json={"title": "Chunked Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert resp.headers.get("Content-Length") is None

    # 4. Side Effects: HEAD does not modify the resource
    @pytest.mark.bug
    def test_head_id_no_side_effects(self, api):
        """Actual: The empty response does not delete or modify the category."""
        cat_id = api.post("/categories", json={"title": "Safe Data"}).json()["id"]

        api.head(f"/categories/{cat_id}")

        check = api.get(f"/categories/{cat_id}")
        assert check.status_code == 200
        assert check.json()["categories"][0]["title"] == "Safe Data"

    # 5. Observed: Empty response regardless of Accept header
    @pytest.mark.bug
    def test_head_id_empty_regardless_of_accept(self, api):
        """Actual: Response is empty regardless of Accept header value."""
        cat_id = api.post("/categories", json={"title": "Accept Test"}).json()["id"]

        for accept in ["application/json", "application/xml"]:
            resp = api.head(f"/categories/{cat_id}", headers={"Accept": accept})
            assert resp.status_code == 200
            assert len(resp.content) == 0
