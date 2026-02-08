"""
test_categories_put.py - Tests for PUT /categories endpoint

Documented behavior:
  - Method not allowed
  - Expected: 405

Tests:
1. Return code (405)
2. Side effects (no data modification)
3. JSON/XML payload attempts
"""

import pytest


class TestCategoriesPut:

    # 1. Capability: Confirm method not allowed
    @pytest.mark.error
    def test_put_categories_returns_405(self, api):
        """Verify PUT /categories returns 405 Method Not Allowed."""
        resp = api.put("/categories", json={"title": "Should Fail"})
        assert resp.status_code == 405

    # 2. Side Effect: No data modification
    @pytest.mark.capability
    def test_put_categories_no_side_effects(self, api):
        """Verify PUT /categories does not modify any data."""
        api.post("/categories", json={"title": "Existing"})
        state_before = api.get("/categories").json()

        api.put("/categories", json={"title": "Should Fail"})

        state_after = api.get("/categories").json()
        assert state_before == state_after

    # 3. Error Case: PUT with JSON payload still rejected
    @pytest.mark.error
    def test_put_categories_json_payload_rejected(self, api):
        """Verify PUT is rejected even with a valid JSON payload."""
        resp = api.put("/categories", json={"title": "Valid JSON"})
        assert resp.status_code == 405

    # 4. Error Case: PUT with XML payload still rejected
    @pytest.mark.error
    def test_put_categories_xml_payload_rejected(self, api):
        """Verify PUT is rejected even with a valid XML payload."""
        xml_data = "<category><title>XML Category</title></category>"
        headers = {"Content-Type": "application/xml"}
        resp = api.put("/categories", data=xml_data, headers=headers)
        assert resp.status_code == 405

    # 5. Error Case: PUT with empty body
    @pytest.mark.error
    def test_put_categories_empty_body_rejected(self, api):
        """Verify PUT is rejected even with an empty body."""
        resp = api.put("/categories")
        assert resp.status_code == 405
