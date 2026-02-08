import pytest

class TestTodosIdPut:

    # 1. Capability: Full Update
    @pytest.mark.capability
    def test_put_update_entire_todo(self, api):
        """Verify that PUT /todos/:id successfully updates all fields of a todo."""
        # Setup: Create a todo
        todo_id = api.post("/todos", json={"title": "Original Title", "description": "Original Desc"}).json()['id']
        
        # Action: Replace with new data
        payload = {"title": "Updated Title", "description": "Updated Desc", "doneStatus": True}
        resp = api.put(f"/todos/{todo_id}", json=payload)
        
        assert resp.status_code == 200
        
        # Verify: Check if the data matches the new payload
        check = api.get(f"/todos/{todo_id}").json()['todos'][0]
        assert check['title'] == "Updated Title"
        assert check['description'] == "Updated Desc"
        # API often returns boolean as strings or specific formats; normalising for check
        assert str(check['doneStatus']).lower() == "true"

    # 2. Capability: Idempotency
    @pytest.mark.capability
    def test_put_is_idempotent(self, api):
        """Verify that sending the same PUT request multiple times has the same effect."""
        todo_id = api.post("/todos", json={"title": "Idempotent Test"}).json()['id']
        payload = {"title": "Same Title", "description": "Fixed"}
        
        # Multiple PUTs
        api.put(f"/todos/{todo_id}", json=payload)
        resp2 = api.put(f"/todos/{todo_id}", json=payload)
        
        assert resp2.status_code == 200
        check = api.get(f"/todos/{todo_id}").json()['todos'][0]
        assert check['title'] == "Same Title"

    # 3. Error Case: Non-Existent ID
    @pytest.mark.error
    def test_put_non_existent_id_error(self, api):
        """Verify that PUT to an ID that does not exist returns 404."""
        # Use an impossible ID to ensure it's not in the DB
        resp = api.put("/todos/-1", json={"title": "Ghost"})
        assert resp.status_code == 404

   # 4. Capability: Required Field Validation
    @pytest.mark.error
    def test_put_missing_title_error(self, api):
        """
        Verify that PUT requires a title. 
        If this passes (returns 400), the API is following strict validation.
        """
        todo_id = api.post("/todos", json={"title": "Valid Title"}).json()['id']
        
        # Action: PUT without 'title'
        resp = api.put(f"/todos/{todo_id}", json={"description": "No title here"})
        
        # If the API returns 400, it's working correctly!
        assert resp.status_code == 400

    # 5. Capability: Data Type Validation
    @pytest.mark.error
    def test_put_invalid_boolean_type_error(self, api):
        """Verify the API rejects incorrect data types for doneStatus."""
        todo_id = api.post("/todos", json={"title": "Type Test"}).json()['id']
        
        # Action: Send string for boolean
        resp = api.put(f"/todos/{todo_id}", json={"doneStatus": "NotABoolean"})
        
        # If the API returns 400, it's working correctly!
        assert resp.status_code == 400