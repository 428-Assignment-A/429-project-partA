import pytest
import requests

class TestTodosUndocumented:

    # 1. Undocumented: PUT on Collection
    @pytest.mark.error
    def test_put_todos_collection_undocumented(self, api):
        """Verify PUT /todos is not implemented (Expected: 404/405)."""
        resp = api.put("/todos", json={"title": "Should fail"})
        # Documentation doesn't list PUT for collection
        assert resp.status_code in [404, 405]

    # 2. Undocumented: DELETE on Collection
    @pytest.mark.error
    def test_delete_todos_collection_undocumented(self, api):
        """Verify DELETE /todos is not implemented."""
        resp = api.delete("/todos")
        assert resp.status_code in [404, 405]

    # 3. Undocumented: PATCH on Collection
    @pytest.mark.error
    def test_patch_todos_collection_undocumented(self, api):
        """Verify PATCH /todos is not implemented."""
        resp = requests.patch(f"{api.url}/todos", json={"title": "Should fail"})
        assert resp.status_code in [404, 405]

    # 4. Undocumented: PATCH on Instance
    @pytest.mark.error
    def test_patch_todo_id_undocumented(self, api):
        """Verify PATCH /todos/:id is not implemented."""
        # Setup: Ensure an ID exists
        todo_id = api.post("/todos", json={"title": "Patch Test"}).json()['id']
        
        resp = requests.patch(f"{api.url}/todos/{todo_id}", json={"title": "New"})
        assert resp.status_code in [404, 405]

    # 5. Side Effect Check: Collection Integrity
    @pytest.mark.capability
    def test_undocumented_methods_do_not_wipe_data(self, api):
        """Safety check: Ensure failed DELETE/PUT didn't actually clear the DB."""
        api.post("/todos", json={"title": "Persistent"})
        
        # Attempt destructive undocumented calls
        api.delete("/todos")
        api.put("/todos", json={})
        
        # Verify data still exists
        resp = api.get("/todos")
        assert len(resp.json()["todos"]) > 0