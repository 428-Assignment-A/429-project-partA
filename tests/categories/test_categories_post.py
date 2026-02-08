"""
test_categories_post.py - Tests for POST /categories endpoint

Documented behavior:
  - Create category without an ID using field values in the body
  - Expected: 201 (created) or 400 (error)

Tests:
1. Core functionality
2. JSON/XML format
3. Return codes
4. Side effects
5. Error cases
6. Bug cases
"""

import pytest


class TestCategoriesPost:

    # 1. Capability: Basic creation with JSON
    @pytest.mark.capability
    def test_post_category_json_capability(self, api):
        """Confirm API creates category using standard JSON fields."""
        payload = {"title": "Standard Category", "description": "Basic test"}
        resp = api.post("/categories", json=payload)

        assert resp.status_code in [200, 201]
        data = resp.json()
        assert data["title"] == "Standard Category"
        assert "id" in data

    # 2. Capability: Long title
    @pytest.mark.capability
    def test_post_category_extreme_length_title(self, api):
        """Confirm API handles extremely long titles (500+ characters)."""
        long_title = "A" * 500
        resp = api.post("/categories", json={"title": long_title})

        assert resp.status_code in [200, 201]
        assert resp.json()["title"] == long_title

    # 3. Capability: Special characters
    @pytest.mark.capability
    def test_post_category_special_chars(self, api):
        """Confirm API handles XSS scripts and international characters."""
        special_title = "<script>alert('xss')</script> & special chars: é, ñ, 中文"
        resp = api.post("/categories", json={"title": special_title})

        assert resp.status_code in [200, 201]
        assert resp.json()["title"] == special_title

    # 4. Format: XML payload creation
    @pytest.mark.capability
    def test_post_category_xml_format(self, api):
        """Verify the API can create a category from an XML payload."""
        xml_data = "<category><title>XML Category</title><description>Created with XML</description></category>"
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}

        resp = api.post("/categories", data=xml_data, headers=headers)

        assert resp.status_code in [200, 201]
        assert "XML Category" in resp.text
        assert "application/xml" in resp.headers["Content-Type"]

    # 5. Error Case: Malformed JSON payload
    @pytest.mark.error
    def test_post_category_malformed_json_error(self, api):
        """Verify API returns 400 for malformed JSON structure."""
        malformed_json = '{"title": "Broken JSON", "description": "missing brace"'
        headers = {"Content-Type": "application/json"}

        resp = api.post("/categories", data=malformed_json, headers=headers)
        assert resp.status_code == 400

    # 6. Error Case: Malformed XML payload
    @pytest.mark.error
    def test_post_category_malformed_xml_error(self, api):
        """Verify API returns 400 for invalid XML structure."""
        malformed_xml = "<category><title>Broken XML</title/category>"
        headers = {"Content-Type": "application/xml"}

        resp = api.post("/categories", data=malformed_xml, headers=headers)
        assert resp.status_code == 400

    # 7. Side Effects: State verification
    @pytest.mark.capability
    def test_post_category_side_effect_count(self, api):
        """Verify that POST only creates one item and doesn't modify others."""
        initial_categories = api.get("/categories").json()["categories"]
        initial_count = len(initial_categories)

        api.post("/categories", json={"title": "Count Test"})

        final_categories = api.get("/categories").json()["categories"]
        assert len(final_categories) == initial_count + 1

        # Confirm old items remain unchanged
        if initial_count > 0:
            assert initial_categories[0] in final_categories

    # 8. Return Code: Correct ID generation
    @pytest.mark.capability
    def test_post_category_id_increment_logic(self, api):
        """Verify generated IDs are unique and incrementing."""
        resp1 = api.post("/categories", json={"title": "First"})
        id1 = int(resp1.json()["id"])

        resp2 = api.post("/categories", json={"title": "Second"})
        id2 = int(resp2.json()["id"])

        assert id2 > id1

    # 9. Return Code: Success code check
    @pytest.mark.capability
    def test_post_category_returns_success_code(self, api):
        """Confirm return code is in the 200-201 range."""
        resp = api.post("/categories", json={"title": "Code Check"})
        assert resp.status_code in [200, 201]

    # 10. Error Case: Empty title string
    @pytest.mark.error
    def test_post_category_empty_title_error(self, api):
        """Verify that an empty title returns 400."""
        resp = api.post("/categories", json={"title": ""})
        assert resp.status_code == 400

    # 11. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="API fails to return 400 for invalid data types")
    def test_post_category_type_validation_expected(self, api):
        """Expected: API should reject non-string titles with 400 Bad Request."""
        payload = {"title": True}
        resp = api.post("/categories", json=payload)
        assert resp.status_code == 400

    # 12. Bug Case: Actual Behavior (PASSING)
    @pytest.mark.bug
    def test_post_category_type_validation_actual(self, api):
        """Actual: API accepts invalid types and returns 201 Created."""
        payload = {"title": True}
        resp = api.post("/categories", json=payload)
        assert resp.status_code == 201
        assert str(resp.json()["title"]) == "true"
