"""
test_categories_id_get.py - Tests for GET /categories/:id endpoint

Documented behavior:
  - Return a specific instance of category using an id
  - Expected: 200 (found) or 404 (not found)

Tests:
1. Core functionality
2. JSON/XML format
3. Return codes
4. Side effects
5. Error cases
"""

import pytest


class TestCategoriesIdGet:

    # 1. Capability: Retrieve specific category
    @pytest.mark.capability
    def test_get_category_by_id_capability(self, api):
        """Confirm GET /categories/:id returns the correct category."""
        cat_id = api.post("/categories", json={"title": "Specific Cat"}).json()["id"]

        resp = api.get(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert "categories" in resp.json()
        assert resp.json()["categories"][0]["title"] == "Specific Cat"

    # 2. Capability: Verify correct data structure
    @pytest.mark.capability
    def test_get_category_by_id_structure(self, api):
        """Verify the response contains expected fields."""
        cat_id = api.post("/categories", json={
            "title": "Structured",
            "description": "Has description"
        }).json()["id"]

        resp = api.get(f"/categories/{cat_id}")
        cat = resp.json()["categories"][0]
        assert "id" in cat
        assert "title" in cat
        assert "description" in cat

    # 3. Format: JSON Response
    @pytest.mark.capability
    def test_get_category_by_id_json_format(self, api):
        """Verify JSON response structure and headers."""
        cat_id = api.post("/categories", json={"title": "JSON Test"}).json()["id"]

        resp = api.get(f"/categories/{cat_id}", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

    # 4. Format: XML Response
    @pytest.mark.capability
    def test_get_category_by_id_xml_format(self, api):
        """Verify XML response structure and headers."""
        cat_id = api.post("/categories", json={"title": "XML Test"}).json()["id"]

        resp = api.get(f"/categories/{cat_id}", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["Content-Type"]
        assert "XML Test" in resp.text

    # 5. Error Case: Non-existent ID
    @pytest.mark.error
    def test_get_category_non_existent_id_error(self, api):
        """Verify 404 returned for a category ID that does not exist."""
        resp = api.get("/categories/99999")
        assert resp.status_code == 404

    # 6. Error Case: Invalid ID formats
    @pytest.mark.error
    @pytest.mark.parametrize("bad_id", [0, -1, "abc"])
    def test_get_category_invalid_id_format_error(self, api, bad_id):
        """Verify 404 for logically invalid ID paths."""
        resp = api.get(f"/categories/{bad_id}")
        assert resp.status_code == 404

    # 7. Side Effects: GET is idempotent
    @pytest.mark.capability
    def test_get_category_by_id_no_side_effects(self, api):
        """Verify that GET /categories/:id does not modify the resource."""
        cat_id = api.post("/categories", json={"title": "Stable"}).json()["id"]
        state_before = api.get(f"/categories/{cat_id}").json()

        api.get(f"/categories/{cat_id}")
        api.get(f"/categories/{cat_id}")

        state_after = api.get(f"/categories/{cat_id}").json()
        assert state_before == state_after

    # 8. Capability: Only returns the requested category
    @pytest.mark.capability
    def test_get_category_by_id_returns_single(self, api):
        """Verify GET /categories/:id returns exactly one category."""
        api.post("/categories", json={"title": "One"})
        cat_id = api.post("/categories", json={"title": "Two"}).json()["id"]

        resp = api.get(f"/categories/{cat_id}")
        assert len(resp.json()["categories"]) == 1
        assert resp.json()["categories"][0]["id"] == str(cat_id)
