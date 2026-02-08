"""
test_categories_id_delete.py - Tests for DELETE /categories/:id endpoint

Documented behavior:
  - Delete a specific instance of category using an id
  - Expected: 200 (deleted) or 404 (not found)

Tests:
1. Core functionality
2. Return codes
3. Side effects
4. Error cases
"""

import pytest


class TestCategoriesIdDelete:

    # 1. Capability: Basic deletion
    @pytest.mark.capability
    def test_delete_category_id_capability(self, api):
        """Confirm we can delete an existing category by ID."""
        cat_id = api.post("/categories", json={"title": "Delete Me"}).json()["id"]

        resp = api.delete(f"/categories/{cat_id}")
        assert resp.status_code == 200

        # Verify: Attempt to GET the deleted ID
        get_resp = api.get(f"/categories/{cat_id}")
        assert get_resp.status_code == 404

    # 2. Side Effect: Data isolation
    @pytest.mark.capability
    def test_delete_category_isolation_side_effect(self, api):
        """Verify deleting one category does not impact others."""
        id_to_keep = api.post("/categories", json={"title": "Keep"}).json()["id"]
        id_to_del = api.post("/categories", json={"title": "Discard"}).json()["id"]

        api.delete(f"/categories/{id_to_del}")

        keep_resp = api.get(f"/categories/{id_to_keep}")
        assert keep_resp.status_code == 200
        assert keep_resp.json()["categories"][0]["title"] == "Keep"

    # 3. Error Case: Non-existent ID
    @pytest.mark.error
    def test_delete_category_not_found_error(self, api):
        """Verify 404 response when trying to delete an ID that doesn't exist."""
        resp = api.delete("/categories/9999")
        assert resp.status_code == 404

    # 4. Error Case: Invalid ID formats
    @pytest.mark.error
    @pytest.mark.parametrize("bad_id", [0, -1, "abc"])
    def test_delete_category_invalid_id_format_error(self, api, bad_id):
        """Verify 404 for logically invalid ID paths."""
        resp = api.delete(f"/categories/{bad_id}")
        assert resp.status_code == 404

    # 5. Side Effect: Collection count logic
    @pytest.mark.capability
    def test_delete_category_decrements_count(self, api):
        """Verify the total collection size decreases by exactly one."""
        cat_id = api.post("/categories", json={"title": "Temp"}).json()["id"]
        initial_count = len(api.get("/categories").json()["categories"])

        api.delete(f"/categories/{cat_id}")

        final_count = len(api.get("/categories").json()["categories"])
        assert final_count == initial_count - 1

    # 6. Format: XML compatibility
    @pytest.mark.capability
    def test_delete_category_response_xml_format(self, api):
        """Verify DELETE request can return an XML response if requested."""
        cat_id = api.post("/categories", json={"title": "XML Delete"}).json()["id"]

        resp = api.delete(f"/categories/{cat_id}", headers={"Accept": "application/xml"})

        assert resp.status_code == 200
        assert "application/xml" in resp.headers["Content-Type"]

    # 7. Capability: Idempotency check (second delete)
    @pytest.mark.error
    def test_delete_category_twice_error(self, api):
        """Verify that deleting the same ID twice returns 404 on the second attempt."""
        cat_id = api.post("/categories", json={"title": "Delete Twice"}).json()["id"]

        api.delete(f"/categories/{cat_id}")  # First time: 200
        resp_two = api.delete(f"/categories/{cat_id}")  # Second time: 404

        assert resp_two.status_code == 404
