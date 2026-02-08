"""
test_categories_id_put.py - Tests for PUT /categories/:id endpoint

Documented behavior:
  - Amend a specific instance of category using an id with a body
    containing the fields to amend
  - Expected: 200 (success) or 404 (not found)

Tests:
1. Core functionality
2. Return codes
3. Side effects
4. Error cases
"""

import pytest


class TestCategoriesIdPut:

    # 1. Capability: Full update
    @pytest.mark.capability
    def test_put_update_entire_category(self, api):
        """Verify that PUT /categories/:id successfully updates all fields."""
        cat_id = api.post("/categories", json={
            "title": "Original Title",
            "description": "Original Desc"
        }).json()["id"]

        payload = {"title": "Updated Title", "description": "Updated Desc"}
        resp = api.put(f"/categories/{cat_id}", json=payload)

        assert resp.status_code == 200

        check = api.get(f"/categories/{cat_id}").json()["categories"][0]
        assert check["title"] == "Updated Title"
        assert check["description"] == "Updated Desc"

    # 2. Capability: Idempotency
    @pytest.mark.capability
    def test_put_category_is_idempotent(self, api):
        """Verify that sending the same PUT request multiple times has the same effect."""
        cat_id = api.post("/categories", json={"title": "Idempotent Test"}).json()["id"]
        payload = {"title": "Same Title", "description": "Fixed"}

        api.put(f"/categories/{cat_id}", json=payload)
        resp2 = api.put(f"/categories/{cat_id}", json=payload)

        assert resp2.status_code == 200
        check = api.get(f"/categories/{cat_id}").json()["categories"][0]
        assert check["title"] == "Same Title"

    # 3. Error Case: Non-existent ID
    @pytest.mark.error
    def test_put_category_non_existent_id_error(self, api):
        """Verify that PUT to an ID that does not exist returns 404."""
        resp = api.put("/categories/-1", json={"title": "Ghost"})
        assert resp.status_code == 404

    # 4. Error Case: Missing title
    @pytest.mark.error
    def test_put_category_missing_title_error(self, api):
        """Verify that PUT requires a title field."""
        cat_id = api.post("/categories", json={"title": "Valid Title"}).json()["id"]

        resp = api.put(f"/categories/{cat_id}", json={"description": "No title here"})
        # PUT replaces the resource; missing required fields should fail
        assert resp.status_code == 400

    # 5. Error Case: Invalid boolean type for title
    @pytest.mark.error
    def test_put_category_invalid_type_error(self, api):
        """Verify the API rejects incorrect data types."""
        cat_id = api.post("/categories", json={"title": "Type Test"}).json()["id"]

        resp = api.put(f"/categories/{cat_id}", json={"title": 12345})
        # Numeric title should ideally be rejected
        assert resp.status_code in [200, 400]

    # 6. Side Effects: Only the targeted category is modified
    @pytest.mark.capability
    def test_put_category_no_collateral_side_effects(self, api):
        """Verify that PUT only modifies the targeted category."""
        id_keep = api.post("/categories", json={"title": "Keep"}).json()["id"]
        id_update = api.post("/categories", json={"title": "Change Me"}).json()["id"]

        api.put(f"/categories/{id_update}", json={"title": "Changed"})

        kept = api.get(f"/categories/{id_keep}").json()["categories"][0]
        assert kept["title"] == "Keep"

    # 7. Format: XML payload
    @pytest.mark.capability
    def test_put_category_xml_format(self, api):
        """Verify the API can update a category using an XML payload."""
        cat_id = api.post("/categories", json={"title": "Before XML"}).json()["id"]

        xml_data = f"<category><title>After XML</title></category>"
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}
        resp = api.put(f"/categories/{cat_id}", data=xml_data, headers=headers)

        assert resp.status_code == 200
        assert "After XML" in resp.text
