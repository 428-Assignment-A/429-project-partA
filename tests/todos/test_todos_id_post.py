import pytest

class TestTodosIdPost:

    # 1. Capability: Update existing Todo via POST
    @pytest.mark.capability
    def test_post_update_todo_title(self, api):
        """Verify that POST /todos/:id can update the title of an existing todo."""
        # Setup: Create a todo
        todo_id = api.post("/todos", json={"title": "Old Title"}).json()['id']
        
        # Action: Update title via POST
        resp = api.post(f"/todos/{todo_id}", json={"title": "New Title"})
        
        assert resp.status_code == 200
        # Verify change
        check = api.get(f"/todos/{todo_id}").json()
        assert check['todos'][0]['title'] == "New Title"

    # 2. Capability: Update description via POST
    @pytest.mark.capability
    def test_post_update_todo_description(self, api):
        """Verify that POST /todos/:id can update the description."""
        todo_id = api.post("/todos", json={"title": "Test"}).json()['id']
        
        payload = {"description": "Updated Description"}
        resp = api.post(f"/todos/{todo_id}", json=payload)
        
        assert resp.status_code == 200
        check = api.get(f"/todos/{todo_id}").json()
        assert check['todos'][0]['description'] == "Updated Description"

    # 3. Error Case: POST to non-existent ID
    @pytest.mark.error
    def test_post_update_non_existent_id(self, api):
        """Verify that POST to an ID that doesn't exist returns 404."""
        resp = api.post("/todos/999999", json={"title": "Ghost Update"})
        assert resp.status_code == 404

    # 4. Capability: POST with partial payload (Patch-like behavior)
    @pytest.mark.capability
    def test_post_partial_update_preserves_other_fields(self, api):
        """
        Verify that POSTing only one field doesn't wipe out the others.
        This tests if the API treats POST :id as a partial update (PATCH).
        """
        # Setup: Create todo with title and description
        todo_id = api.post("/todos", json={
            "title": "Stay", 
            "description": "Don't Delete Me"
        }).json()['id']
        
        # Action: Update only the title
        api.post(f"/todos/{todo_id}", json={"title": "Change"})
        
        # Verify: Description should still be there
        check = api.get(f"/todos/{todo_id}").json()
        assert check['todos'][0]['title'] == "Change"
        assert check['todos'][0]['description'] == "Don't Delete Me"

    # 5. Error Case: POST with invalid field
    @pytest.mark.error
    def test_post_update_with_invalid_field(self, api):
        """Verify the API handles (or ignores) unknown fields in the payload."""
        todo_id = api.post("/todos", json={"title": "Valid"}).json()['id']
        
        resp = api.post(f"/todos/{todo_id}", json={"extra_field": "not real"})
        # Most APIs return 200/400; we check if it remains stable
        assert resp.status_code in [200, 400]

    # 6. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: Update endpoint fails to return 400 for invalid data types (Boolean as Title)")
    def test_post_update_type_validation_expected(self, api):
        """Expected: Reject boolean title with 400."""
        todo_id = api.post("/todos", json={"title": "Init"}).json()['id']
        resp = api.post(f"/todos/{todo_id}", json={"title": True})
        assert resp.status_code == 400

    # 7. Error Case: Malformed JSON Syntax
    @pytest.mark.error
    def test_post_update_malformed_json(self, api):
        """Verify 400 for broken JSON syntax during update."""
        todo_id = api.post("/todos", json={"title": "Init"}).json()['id']
        broken_json = '{"title": "oops"' # Missing closing brace
        resp = api.post(f"/todos/{todo_id}", data=broken_json, headers={"Content-Type": "application/json"})
        assert resp.status_code == 400
