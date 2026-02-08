"""
test_categories_id_head_expected.py - Expected behavior for HEAD /categories/:id

Bug: HEAD /categories/:id is documented as returning headers for a specific
instance of category using an id. The endpoint should've returned all the
headers for the instances of category of a specific ID, but instead returned
200 OK with an empty response.

Observed: 200 OK with empty response.

Module 1 (Expected Behavior - FAILING):
  Tests what the documentation says SHOULD happen.
  All tests are marked xfail because the API does not match expectations.
"""

import pytest


class TestCategoriesIdHeadExpected:

    # 1. Core Functionality: Should return headers for a specific category
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories/:id returns empty response instead of headers for the category instance")
    def test_head_id_returns_headers_for_instance(self, api):
        """Expected: HEAD /categories/:id should return headers describing the specific category."""
        cat_id = api.post("/categories", json={"title": "Head Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 2. Return Code: HEAD should mirror GET headers
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories/:id returns empty response, headers don't match GET")
    def test_head_id_headers_match_get(self, api):
        """Expected: HEAD should return the same headers as GET (Content-Type, Content-Length)."""
        cat_id = api.post("/categories", json={"title": "Mirror Test"}).json()["id"]

        get_resp = api.get(f"/categories/{cat_id}")
        head_resp = api.head(f"/categories/{cat_id}")

        assert head_resp.status_code == 200
        assert "Content-Type" in head_resp.headers
        assert "Content-Length" in head_resp.headers
        assert int(head_resp.headers["Content-Length"]) == len(get_resp.content)

    # 3. Format: JSON Content-Type header
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories/:id returns empty response")
    def test_head_id_json_content_type(self, api):
        """Expected: HEAD with Accept: application/json should return JSON Content-Type and size."""
        cat_id = api.post("/categories", json={"title": "JSON Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 4. Format: XML Content-Type header
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories/:id returns empty response")
    def test_head_id_xml_content_type(self, api):
        """Expected: HEAD with Accept: application/xml should return XML Content-Type and size."""
        cat_id = api.post("/categories", json={"title": "XML Test"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 5. Side Effects: HEAD should not modify the resource
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories/:id returns empty response instead of headers for category instance")
    def test_head_id_safe_with_headers(self, api):
        """Expected: HEAD returns headers for the specific category without modifying data."""
        cat_id = api.post("/categories", json={"title": "Safe"}).json()["id"]

        resp = api.head(f"/categories/{cat_id}")

        check = api.get(f"/categories/{cat_id}")
        assert check.json()["categories"][0]["title"] == "Safe"
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0
