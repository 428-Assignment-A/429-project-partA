"""
test_categories_delete.py - Tests for DELETE /categories endpoint

Documented behavior:
  - Method not allowed
  - Expected: 405

Tests:
1. Return code (405)
2. Side effects (no data modification)
"""

import pytest


class TestCategoriesDelete:

    # 1. Capability: Confirm method not allowed
    @pytest.mark.error
    def test_delete_categories_returns_405(self, api):
        """Verify DELETE /categories returns 405 Method Not Allowed."""
        resp = api.delete("/categories")
        assert resp.status_code == 405

    # 2. Side Effect: No data modification
    @pytest.mark.capability
    def test_delete_categories_no_side_effects(self, api):
        """Verify DELETE /categories does not wipe any data."""
        api.post("/categories", json={"title": "Persistent"})
        state_before = api.get("/categories").json()

        api.delete("/categories")

        state_after = api.get("/categories").json()
        assert state_before == state_after

    # 3. Side Effect: Data survives failed DELETE
    @pytest.mark.capability
    def test_delete_categories_data_survives(self, api):
        """Safety check: Ensure failed DELETE didn't actually clear the DB."""
        api.post("/categories", json={"title": "Survivor"})

        api.delete("/categories")

        resp = api.get("/categories")
        assert len(resp.json()["categories"]) > 0

    # 4. Error Case: DELETE with query params still rejected
    @pytest.mark.error
    def test_delete_categories_with_params_rejected(self, api):
        """Verify DELETE is rejected even with query parameters."""
        resp = api.delete("/categories?title=Something")
        assert resp.status_code == 405
