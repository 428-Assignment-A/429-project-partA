"""
test_categories_get.py - Tests for GET /categories endpoint

Documented behavior:
  - Returns all instances of category
  - Expected: 200

Tests:
1. Core functionality
2. JSON/XML format
3. Return codes
4. Side effects
5. Query parameter filtering
"""

import pytest


class TestCategoriesGet:

    # 1. Capability: Return all instances
    @pytest.mark.capability
    def test_get_all_categories_capability(self, api):
        """Confirm GET /categories returns the list of all categories."""
        resp = api.get("/categories")
        assert resp.status_code == 200
        assert "categories" in resp.json()
        assert isinstance(resp.json()["categories"], list)

    # 2. Capability: Verify returned data matches created data
    @pytest.mark.capability
    def test_get_categories_contains_created_item(self, api):
        """Verify a newly created category appears in the GET response."""
        api.post("/categories", json={"title": "TestCategory"})

        resp = api.get("/categories")
        titles = [c["title"] for c in resp.json()["categories"]]
        assert "TestCategory" in titles

    # 3. Capability: Long title support
    @pytest.mark.capability
    def test_get_categories_contains_long_title(self, api):
        """Verify the API can store and return an extremely long title."""
        long_title = "A" * 500
        api.post("/categories", json={"title": long_title})

        resp = api.get("/categories")
        titles = [c["title"] for c in resp.json()["categories"]]
        assert long_title in titles

    # 4. Capability: Special characters support
    @pytest.mark.capability
    def test_get_categories_contains_special_chars(self, api):
        """Verify the API stores and returns XSS scripts and special characters."""
        special = "<script>alert('xss')</script> & special chars: é, ñ, 中文"
        api.post("/categories", json={"title": special})

        resp = api.get("/categories")
        titles = [c["title"] for c in resp.json()["categories"]]
        assert special in titles

    # 5. Command Line Query: Filter by title
    @pytest.mark.capability
    def test_get_categories_filter_by_title(self, api):
        """Verify filtering via query parameters: /categories?title=..."""
        unique_title = "FilterMeCategory123"
        api.post("/categories", json={"title": unique_title})

        resp = api.get(f"/categories?title={unique_title}")
        assert resp.status_code == 200
        for cat in resp.json()["categories"]:
            assert cat["title"] == unique_title

    # 6. Command Line Query: Filter by description
    @pytest.mark.capability
    def test_get_categories_filter_by_description(self, api):
        """Verify filtering via query parameters: /categories?description=..."""
        unique_desc = "UniqueCategoryDesc"
        api.post("/categories", json={"title": "Test", "description": unique_desc})

        resp = api.get(f"/categories?description={unique_desc}")
        assert resp.status_code == 200
        for cat in resp.json()["categories"]:
            assert cat["description"] == unique_desc

    # 7. Format: JSON Response
    @pytest.mark.capability
    def test_get_categories_json_format(self, api):
        """Verify JSON response structure and headers."""
        resp = api.get("/categories", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

    # 8. Format: XML Response
    @pytest.mark.capability
    def test_get_categories_xml_format(self, api):
        """Verify XML response structure and headers."""
        resp = api.get("/categories", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["Content-Type"]
        assert "<categories>" in resp.text

    # 9. Side Effects: GET is idempotent
    @pytest.mark.capability
    def test_get_categories_no_side_effects(self, api):
        """Verify that GET /categories does not modify any data."""
        api.post("/categories", json={"title": "Stable"})
        state_before = api.get("/categories").json()

        api.get("/categories")
        api.get("/categories")

        state_after = api.get("/categories").json()
        assert state_before == state_after

    # 10. Error Case: Filter returns empty results
    @pytest.mark.error
    def test_get_categories_filter_no_results(self, api):
        """Verify filtering for a non-existent item returns an empty list."""
        resp = api.get("/categories?title=ThisTitleShouldNotExist12345")
        assert resp.status_code == 200
        assert len(resp.json()["categories"]) == 0

    # 11. Error Case: Malformed Accept header
    @pytest.mark.error
    def test_get_categories_malformed_accept_header(self, api):
        """Verify behavior when Accept header is nonsense."""
        resp = api.get("/categories", headers={"Accept": "not-a-real-format"})
        assert resp.status_code in [200, 406]
