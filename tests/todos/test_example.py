"""
Example test file - Team members can copy this as a template
"""
import pytest

class TestExample:
    
    def test_get_todos(self, api):
        """Test GET /todos returns 200"""
        response = api.get("/todos")
        assert response.status_code == 200
    
    def test_create_todo(self, api):
        """Test POST /todos creates todo"""
        response = api.post("/todos", json={
            "title": "Test Todo",
            "doneStatus": False
        })
        assert response.status_code == 201
        
        # Cleanup
        todo_id = response.json()["id"]
        api.delete(f"/todos/{todo_id}")
