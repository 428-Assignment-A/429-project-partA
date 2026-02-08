"""
test_categories_undocumented.py - Tests for undocumented /categories endpoints

Undocumented endpoints:
  /categories       PUT, DELETE, OPTIONS, PATCH
  /categories/:id   OPTIONS, PATCH

Tests:
1. Verify undocumented methods return 404/405
2. Side effect check: data integrity after failed calls
"""

import pytest
import requests


class TestCategoriesUndocumented:

    # 1. Undocumented: PUT on Collection
    @pytest.mark.error
    def test_put_categories_collection_undocumented(self, api):
        """Verify PUT /categories is not implemented (Expected: 404/405)."""
        resp = api.put("/categories", json={"title": "Should fail"})
        assert resp.status_code in [404, 405]

    # 2. Undocumented: DELETE on Collection
    @pytest.mark.error
    def test_delete_categories_collection_undocumented(self, api):
        """Verify DELETE /categories is not implemented."""
        resp = api.delete("/categories")
        assert resp.status_code in [404, 405]

    # 3. Undocumented: OPTIONS on Collection
    @pytest.mark.error
    def test_options_categories_collection_undocumented(self, api):
        """Verify OPTIONS /categories is not documented but returns discovered behavior."""
        resp = api.options("/categories")
        # Undocumented: the API still responds, likely 200 with Allow header
        assert resp.status_code in [200, 404, 405]

    # 4. Undocumented: PATCH on Collection
    @pytest.mark.error
    def test_patch_categories_collection_undocumented(self, api):
        """Verify PATCH /categories is not implemented."""
        resp = requests.patch(f"{api.url}/categories", json={"title": "Should fail"})
        assert resp.status_code in [404, 405]

    # 5. Undocumented: OPTIONS on Instance
    @pytest.mark.error
    def test_options_categories_id_undocumented(self, api):
        """Verify OPTIONS /categories/:id is not documented but returns discovered behavior."""
        cat_id = api.post("/categories", json={"title": "Options Test"}).json()["id"]

        resp = api.options(f"/categories/{cat_id}")
        # Undocumented: the API still responds, likely 200 with Allow header
        assert resp.status_code in [200, 404, 405]

    # 6. Undocumented: PATCH on Instance
    @pytest.mark.error
    def test_patch_categories_id_undocumented(self, api):
        """Verify PATCH /categories/:id is not implemented."""
        cat_id = api.post("/categories", json={"title": "Patch Test"}).json()["id"]

        resp = requests.patch(f"{api.url}/categories/{cat_id}", json={"title": "New"})
        assert resp.status_code in [404, 405]

    # 7. Side Effect Check: Collection Integrity
    @pytest.mark.capability
    def test_undocumented_methods_do_not_wipe_data(self, api):
        """Safety check: Ensure failed DELETE/PUT didn't actually clear the DB."""
        api.post("/categories", json={"title": "Persistent"})

        # Attempt destructive undocumented calls
        api.delete("/categories")
        api.put("/categories", json={})

        # Verify data still exists
        resp = api.get("/categories")
        assert len(resp.json()["categories"]) > 0
