"""
test_categories_id_post.py - Tests for POST /categories/:id endpoint

Documented behavior:
  - Amend a specific instance of category using an id with a body
    containing the fields to amend
  - Expected: 200 (success) or 404 (not found)

Tests:
1. Core functionality
2. Return codes
3. Side effects
4. Error cases
5. Bug cases
"""

import pytest


class TestCategoriesIdPost:

    # 1. Capability: Update existing category via POST
    @pytest.mark.capability
    def test_post_update_category_title(self, api):
        """Verify that POST /categories/:id can update the title."""
        cat_id = api.post("/categories", json={"title": "Old Title"}).json()["id"]

        resp = api.post(f"/categories/{cat_id}", json={"title": "New Title"})
        assert resp.status_code == 200

        check = api.get(f"/categories/{cat_id}").json()
        assert check["categories"][0]["title"] == "New Title"

    # 2. Capability: Update description via POST
    @pytest.mark.capability
    def test_post_update_category_description(self, api):
        """Verify that POST /categories/:id can update the description."""
        cat_id = api.post("/categories", json={"title": "Test"}).json()["id"]

        resp = api.post(f"/categories/{cat_id}", json={"description": "Updated Description"})
        assert resp.status_code == 200

        check = api.get(f"/categories/{cat_id}").json()
        assert check["categories"][0]["description"] == "Updated Description"

    # 3. Error Case: POST to non-existent ID
    @pytest.mark.error
    def test_post_update_non_existent_id(self, api):
        """Verify that POST to an ID that doesn't exist returns 404."""
        resp = api.post("/categories/999999", json={"title": "Ghost Update"})
        assert resp.status_code == 404

    # 4. Capability: POST with partial payload preserves other fields
    @pytest.mark.capability
    def test_post_partial_update_preserves_other_fields(self, api):
        """
        Verify that POSTing only one field doesn't wipe out others.
        Tests if the API treats POST :id as a partial update (PATCH-like).
        """
        cat_id = api.post("/categories", json={
            "title": "Stay",
            "description": "Don't Delete Me"
        }).json()["id"]

        api.post(f"/categories/{cat_id}", json={"title": "Changed"})

        check = api.get(f"/categories/{cat_id}").json()
        assert check["categories"][0]["title"] == "Changed"
        assert check["categories"][0]["description"] == "Don't Delete Me"

    # 5. Error Case: POST with invalid field
    @pytest.mark.error
    def test_post_update_with_invalid_field(self, api):
        """Verify the API handles unknown fields in the payload."""
        cat_id = api.post("/categories", json={"title": "Valid"}).json()["id"]

        resp = api.post(f"/categories/{cat_id}", json={"extra_field": "not real"})
        assert resp.status_code in [200, 400]

    # 6. Error Case: Malformed JSON syntax
    @pytest.mark.error
    def test_post_update_malformed_json(self, api):
        """Verify 400 for broken JSON syntax during update."""
        cat_id = api.post("/categories", json={"title": "Init"}).json()["id"]
        broken_json = '{"title": "oops"'
        resp = api.post(f"/categories/{cat_id}", data=broken_json,
                        headers={"Content-Type": "application/json"})
        assert resp.status_code == 400

    # 7. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: Update endpoint fails to return 400 for invalid data types (Boolean as Title)")
    def test_post_update_type_validation_expected(self, api):
        """Expected: Reject boolean title with 400."""
        cat_id = api.post("/categories", json={"title": "Init"}).json()["id"]
        resp = api.post(f"/categories/{cat_id}", json={"title": True})
        assert resp.status_code == 400

    # 8. Side Effects: Only the targeted category is modified
    @pytest.mark.capability
    def test_post_update_no_collateral_side_effects(self, api):
        """Verify POST update only modifies the targeted category."""
        id_keep = api.post("/categories", json={"title": "Keep"}).json()["id"]
        id_update = api.post("/categories", json={"title": "Change Me"}).json()["id"]

        api.post(f"/categories/{id_update}", json={"title": "Changed"})

        kept = api.get(f"/categories/{id_keep}").json()["categories"][0]
        assert kept["title"] == "Keep"

    # 9. Format: XML payload update
    @pytest.mark.capability
    def test_post_update_category_xml_format(self, api):
        """Verify the API can update a category using an XML payload."""
        cat_id = api.post("/categories", json={"title": "Before XML"}).json()["id"]

        xml_data = "<category><title>After XML</title></category>"
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}
        resp = api.post(f"/categories/{cat_id}", data=xml_data, headers=headers)

        assert resp.status_code == 200
        assert "After XML" in resp.text
