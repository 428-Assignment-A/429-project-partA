"""
test_categories_id_options_expected.py - Expected behavior for OPTIONS /categories/:id

Bug: This endpoint was not documented in the official docs, but the swagger
json description indicates it should show all the options for the endpoints
for categories of a specific ID. The endpoint returns an empty response instead.

Module 1 (Expected Behavior - FAILING):
  Tests what the documentation says SHOULD happen.
  All tests are marked xfail because the API does not match expectations.
"""

import pytest


class TestCategoriesIdOptionsExpected:

    # 1. Core Functionality: Should return options/discovery info
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories/:id returns empty body instead of discovery payload")
    def test_options_id_returns_discovery_body(self, api):
        """Expected: OPTIONS /categories/:id should return a non-empty body describing available methods."""
        cat_id = api.post("/categories", json={"title": "Options Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert len(resp.text.strip()) > 0

    # 2. Return Code: Should return 200 with Allow header and body
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories/:id body is empty, missing discovery payload")
    def test_options_id_has_allow_header_and_body(self, api):
        """Expected: Response includes both an 'Allow' header and a descriptive body."""
        cat_id = api.post("/categories", json={"title": "Header Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert "Allow" in resp.headers
        assert len(resp.text.strip()) > 0

    # 3. Format: JSON discovery response
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories/:id returns empty body, cannot verify JSON format")
    def test_options_id_json_discovery(self, api):
        """Expected: OPTIONS should return JSON discovery body when Accept: application/json."""
        cat_id = api.post("/categories", json={"title": "JSON Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert len(resp.text.strip()) > 0

    # 4. Format: XML discovery response
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories/:id returns empty body, cannot verify XML format")
    def test_options_id_xml_discovery(self, api):
        """Expected: OPTIONS should return XML discovery body when Accept: application/xml."""
        cat_id = api.post("/categories", json={"title": "XML Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert len(resp.text.strip()) > 0

    # 5. Side Effects: OPTIONS should not modify the resource
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /categories/:id returns empty body instead of discovery payload")
    def test_options_id_safe_with_content(self, api):
        """Expected: OPTIONS returns discovery info without modifying data."""
        cat_id = api.post("/categories", json={"title": "Stable"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")

        check = api.get(f"/categories/{cat_id}")
        assert check.json()["categories"][0]["title"] == "Stable"
        assert len(resp.text.strip()) > 0
