import pytest

class TestTodosIdDelete:

    # 1. Capability: Basic Deletion
    @pytest.mark.capability
    def test_delete_todo_id_capability(self, api):
        """Confirm we can delete an existing todo by ID."""
        # Setup: Create a todo
        todo_id = api.post("/todos", json={"title": "Delete Me"}).json()["id"]
        
        # Execute
        resp = api.delete(f"/todos/{todo_id}")
        assert resp.status_code == 200
        
        # Verify: Attempt to GET the deleted ID
        get_resp = api.get(f"/todos/{todo_id}")
        assert get_resp.status_code == 404

    # 2. Side Effect: Data Isolation
    @pytest.mark.capability
    def test_delete_todo_isolation_side_effect(self, api):
        """Verify deleting one todo does not impact others in the collection."""
        # Setup: Create two todos
        id_to_keep = api.post("/todos", json={"title": "Keep"}).json()["id"]
        id_to_del = api.post("/todos", json={"title": "Discard"}).json()["id"]
        
        # Execute
        api.delete(f"/todos/{id_to_del}")
        
        # Verify: The other one still exists
        keep_resp = api.get(f"/todos/{id_to_keep}")
        assert keep_resp.status_code == 200
        assert keep_resp.json()["todos"][0]["title"] == "Keep"

    # 3. Error Case: Non-existent ID
    @pytest.mark.error
    def test_delete_id_not_found_error(self, api):
        """Verify 404 response when trying to delete an ID that doesn't exist."""
        resp = api.delete("/todos/9999")
        assert resp.status_code == 404

    # 4. Error Case: Invalid ID Formats
    @pytest.mark.error
    @pytest.mark.parametrize("bad_id", [0, -1, "abc"])
    def test_delete_invalid_id_format_error(self, api, bad_id):
        """Verify 404 for logically invalid ID paths."""
        resp = api.delete(f"/todos/{bad_id}")
        assert resp.status_code == 404

    # 5. Side Effect: Collection Count Logic
    @pytest.mark.capability
    def test_delete_decrements_count_side_effect(self, api):
        """Verify the total collection size decreases by exactly one."""
        # Setup
        todo_id = api.post("/todos", json={"title": "Temp"}).json()["id"]
        initial_count = len(api.get("/todos").json()["todos"])
        
        # Execute
        api.delete(f"/todos/{todo_id}")
        
        # Verify
        final_count = len(api.get("/todos").json()["todos"])
        assert final_count == initial_count - 1

    # 6. Format: XML Compatibility
    @pytest.mark.capability
    def test_delete_response_xml_format(self, api):
        """Verify DELETE request can return an XML response if requested."""
        todo_id = api.post("/todos", json={"title": "XML Delete"}).json()["id"]
        
        # Passing headers to the updated conftest api.delete
        resp = api.delete(f"/todos/{todo_id}", headers={"Accept": "application/xml"})
        
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["Content-Type"]

    # 7. Capability: Idempotency check (Second delete)
    @pytest.mark.error
    def test_delete_twice_error(self, api):
        """Verify that deleting the same ID twice returns a 404 on the second attempt."""
        todo_id = api.post("/todos", json={"title": "Delete Twice"}).json()["id"]
        
        api.delete(f"/todos/{todo_id}") # First time: 200
        resp_two = api.delete(f"/todos/{todo_id}") # Second time: 404
        
        assert resp_two.status_code == 404