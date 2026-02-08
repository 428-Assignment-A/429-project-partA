"""
test_categories_patch.py - Tests for PATCH /categories endpoint

Documented behavior:
  - Method not allowed
  - Expected: 405

Tests:
1. Return code (405)
2. Side effects (no data modification)
"""

import pytest
import requests


class TestCategoriesPatch:

    # 1. Capability: Confirm method not allowed
    @pytest.mark.error
    def test_patch_categories_returns_405(self, api):
        """Verify PATCH /categories returns 405 Method Not Allowed."""
        resp = requests.patch(f"{api.url}/categories", json={"title": "Should Fail"})
        assert resp.status_code == 405

    # 2. Side Effect: No data modification
    @pytest.mark.capability
    def test_patch_categories_no_side_effects(self, api):
        """Verify PATCH /categories does not modify any data."""
        api.post("/categories", json={"title": "Existing"})
        state_before = api.get("/categories").json()

        requests.patch(f"{api.url}/categories", json={"title": "Should Fail"})

        state_after = api.get("/categories").json()
        assert state_before == state_after

    # 3. Error Case: PATCH with JSON payload still rejected
    @pytest.mark.error
    def test_patch_categories_json_payload_rejected(self, api):
        """Verify PATCH is rejected even with a valid JSON payload."""
        resp = requests.patch(f"{api.url}/categories", json={"title": "Valid JSON"})
        assert resp.status_code == 405

    # 4. Error Case: PATCH with XML payload still rejected
    @pytest.mark.error
    def test_patch_categories_xml_payload_rejected(self, api):
        """Verify PATCH is rejected even with a valid XML payload."""
        xml_data = "<category><title>XML Category</title></category>"
        headers = {"Content-Type": "application/xml"}
        resp = requests.patch(f"{api.url}/categories", data=xml_data, headers=headers)
        assert resp.status_code == 405

    # 5. Error Case: PATCH with empty body
    @pytest.mark.error
    def test_patch_categories_empty_body_rejected(self, api):
        """Verify PATCH is rejected even with an empty body."""
        resp = requests.patch(f"{api.url}/categories")
        assert resp.status_code == 405
