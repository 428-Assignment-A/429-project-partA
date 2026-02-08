"""
test_categories_head_expected.py - Expected behavior for HEAD /categories

Bug: HEAD /categories is documented as returning headers for all the instances
of category. The body in the response was empty when it should've returned all
the headers for the instances of category.

Observed: 200 OK with empty response.

Module 1 (Expected Behavior - FAILING):
  Tests what the documentation says SHOULD happen.
  All tests are marked xfail because the API does not match expectations.
"""

import pytest


class TestCategoriesHeadExpected:

    # 1. Core Functionality: Should return headers for all category instances
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories returns empty response instead of headers for all category instances")
    def test_head_categories_returns_headers_for_instances(self, api):
        """Expected: HEAD /categories should return headers describing all category instances."""
        api.post("/categories", json={"title": "Category A"})

        resp = api.head("/categories")
        assert resp.status_code == 200
        # HEAD should return Content-Length indicating the size of the category data
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 2. Return Code: HEAD should mirror GET headers
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories returns empty response, headers don't match GET")
    def test_head_categories_headers_match_get(self, api):
        """Expected: HEAD should return the same headers as GET (Content-Type, Content-Length)."""
        api.post("/categories", json={"title": "Mirror Test"})

        get_resp = api.get("/categories")
        head_resp = api.head("/categories")

        assert head_resp.status_code == 200
        assert "Content-Type" in head_resp.headers
        assert "Content-Length" in head_resp.headers
        assert int(head_resp.headers["Content-Length"]) == len(get_resp.content)

    # 3. Format: JSON Content-Type header
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories returns empty response")
    def test_head_categories_json_content_type(self, api):
        """Expected: HEAD with Accept: application/json should return JSON Content-Type and size."""
        resp = api.head("/categories", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 4. Format: XML Content-Type header
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories returns empty response")
    def test_head_categories_xml_content_type(self, api):
        """Expected: HEAD with Accept: application/xml should return XML Content-Type and size."""
        resp = api.head("/categories", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 5. Side Effects: HEAD should not modify data
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /categories returns empty response instead of headers for category instances")
    def test_head_categories_safe_with_headers(self, api):
        """Expected: HEAD returns headers for all category instances without modifying data."""
        api.post("/categories", json={"title": "Stable"})
        initial = api.get("/categories").json()

        resp = api.head("/categories")

        after = api.get("/categories").json()
        assert initial == after
        # Should have returned headers describing the category instances
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0
