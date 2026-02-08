"""
test_categories_id_patch.py - Tests for PATCH /categories/:id endpoint

Documented behavior:
  - Method not allowed
  - Expected: 405

Tests:
1. Return code (405)
2. Side effects (no data modification)
"""

import pytest
import requests


class TestCategoriesIdPatch:

    # 1. Capability: Confirm method not allowed
    @pytest.mark.error
    def test_patch_category_id_returns_405(self, api):
        """Verify PATCH /categories/:id returns 405 Method Not Allowed."""
        cat_id = api.post("/categories", json={"title": "Patch Test"}).json()["id"]

        resp = requests.patch(f"{api.url}/categories/{cat_id}", json={"title": "New"})
        assert resp.status_code == 405

    # 2. Side Effect: No data modification
    @pytest.mark.capability
    def test_patch_category_id_no_side_effects(self, api):
        """Verify PATCH /categories/:id does not modify the category."""
        cat_id = api.post("/categories", json={"title": "Original"}).json()["id"]

        requests.patch(f"{api.url}/categories/{cat_id}", json={"title": "Patched"})

        check = api.get(f"/categories/{cat_id}").json()["categories"][0]
        assert check["title"] == "Original"

    # 3. Error Case: PATCH with JSON payload still rejected
    @pytest.mark.error
    def test_patch_category_id_json_payload_rejected(self, api):
        """Verify PATCH is rejected even with a valid JSON payload."""
        cat_id = api.post("/categories", json={"title": "JSON Test"}).json()["id"]

        resp = requests.patch(f"{api.url}/categories/{cat_id}", json={"title": "Valid JSON"})
        assert resp.status_code == 405

    # 4. Error Case: PATCH with XML payload still rejected
    @pytest.mark.error
    def test_patch_category_id_xml_payload_rejected(self, api):
        """Verify PATCH is rejected even with a valid XML payload."""
        cat_id = api.post("/categories", json={"title": "XML Test"}).json()["id"]

        xml_data = "<category><title>XML Category</title></category>"
        headers = {"Content-Type": "application/xml"}
        resp = requests.patch(f"{api.url}/categories/{cat_id}", data=xml_data, headers=headers)
        assert resp.status_code == 405

    # 5. Error Case: PATCH with empty body
    @pytest.mark.error
    def test_patch_category_id_empty_body_rejected(self, api):
        """Verify PATCH is rejected even with an empty body."""
        cat_id = api.post("/categories", json={"title": "Empty Test"}).json()["id"]

        resp = requests.patch(f"{api.url}/categories/{cat_id}")
        assert resp.status_code == 405
