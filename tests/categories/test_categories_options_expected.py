"""
test_categories_options_expected.py - Expected behavior for OPTIONS /categories

Bug: This endpoint was not documented in the official docs, but the swagger
json description indicates it should show all the options for the endpoints
for categories. The endpoint returns an empty response instead.

Module 1 (Expected Behavior - FAILING):
  Tests what the documentation says SHOULD happen.
  All tests are marked xfail because the API does not match expectations.
"""

import pytest


class TestCategoriesOptionsExpected:

    # 1. Core Functionality: Should return options/discovery info
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories returns empty body instead of discovery payload")
    def test_options_categories_returns_discovery_body(self, api):
        """Expected: OPTIONS /categories should return a non-empty body describing available methods."""
        resp = api.options("/categories")
        assert resp.status_code == 200
        assert len(resp.text.strip()) > 0

    # 2. Return Code: Should return 200 with Allow header and body
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories body is empty, missing discovery payload")
    def test_options_categories_has_allow_header_and_body(self, api):
        """Expected: Response includes both an 'Allow' header and a descriptive body."""
        resp = api.options("/categories")
        assert resp.status_code == 200
        assert "Allow" in resp.headers
        # The body should describe what each method does
        assert len(resp.text.strip()) > 0

    # 3. Format: JSON discovery response
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories returns empty body, cannot verify JSON format")
    def test_options_categories_json_discovery(self, api):
        """Expected: OPTIONS should return a JSON body when Accept: application/json is specified."""
        resp = api.options("/categories", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert len(resp.text.strip()) > 0

    # 4. Format: XML discovery response
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories returns empty body, cannot verify XML format")
    def test_options_categories_xml_discovery(self, api):
        """Expected: OPTIONS should return an XML body when Accept: application/xml is specified."""
        resp = api.options("/categories", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert len(resp.text.strip()) > 0

    # 5. Side Effects: OPTIONS should not modify data
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories returns empty body instead of discovery payload")
    def test_options_categories_safe_with_content(self, api):
        """Expected: OPTIONS returns discovery info without modifying data."""
        api.post("/categories", json={"title": "Stable"})
        initial = api.get("/categories").json()

        resp = api.options("/categories")

        after = api.get("/categories").json()
        assert initial == after
        # And the response should contain discovery content
        assert len(resp.text.strip()) > 0
