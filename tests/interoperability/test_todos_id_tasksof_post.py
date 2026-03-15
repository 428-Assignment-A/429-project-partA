"""
test_todos_id_tasksof_post.py - Tests for POST /todos/:id/tasksof endpoint

Documented behavior:
  - Creates a relationship named 'tasksof' between a todo and a project
  - Todo becomes a task of the project
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid todo and project (201)
2. Verify relationship exists after creation
3. Create relationship with non-existent todo (404)
4. Create relationship with non-existent project (404)
5. Create duplicate relationship (should succeed)
6. Verify JSON response format
7. Verify no side effects on todo or project data
8. Test malformed JSON - missing id field - BUG
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestTodosIdTasksofPost:
    
    @pytest.mark.capability
    def test_create_tasksof_relationship_valid_ids(self, api):
        """Verify POST /todos/:id/tasksof creates relationship."""
        todo = api.post("/todos", json={"title": "TaskTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        resp = api.post(f"/todos/{todo}/tasksof", json={"id": project})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /todos/:id/tasksof should return the project."""
        todo = api.post("/todos", json={"title": "VerifyTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "VerifyProject"}).json()["id"]
        
        api.post(f"/todos/{todo}/tasksof", json={"id": project})
        
        resp = api.get(f"/todos/{todo}/tasksof")
        assert resp.status_code == 200
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert project in project_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_todo_returns_404(self, api):
        """Verify POST /todos/:id/tasksof returns 404 for unknown todo."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.post("/todos/999999/tasksof", json={"id": project})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_project_returns_404(self, api):
        """Verify POST /todos/:id/tasksof returns 404 for unknown project."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.post(f"/todos/{todo}/tasksof", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same tasksof relationship twice should not fail."""
        todo = api.post("/todos", json={"title": "DupTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "DupProject"}).json()["id"]
        
        first = api.post(f"/todos/{todo}/tasksof", json={"id": project})
        assert first.status_code == 201
        
        second = api.post(f"/todos/{todo}/tasksof", json={"id": project})
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /todos/:id/tasksof returns JSON response."""
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        
        resp = api.post(f"/todos/{todo}/tasksof", json={"id": project})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_entities(self, api):
        """Creating relationship should not modify todo or project data."""
        todo_data = {"title": "OriginalTodo", "description": "Keep this"}
        project_data = {"title": "OriginalProject", "description": "Keep this too"}
        
        todo = api.post("/todos", json=todo_data).json()
        project = api.post("/projects", json=project_data).json()
        
        todo_id = todo["id"]
        project_id = project["id"]
        
        # Get original state
        original_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        original_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        
        # Create relationship
        api.post(f"/todos/{todo_id}/tasksof", json={"id": project_id})
        
        # Verify data unchanged
        after_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        after_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        
        assert original_todo["title"] == after_todo["title"]
        assert original_project["title"] == after_project["title"]
    
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: API accepts empty body and returns 201 instead of 400")
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify POST /todos/:id/tasksof returns 400 when id field is missing.
        
        Expected: 400 Bad Request
        Actual: 201 Created (accepts empty body)
        """
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.post(f"/todos/{todo}/tasksof", json={})
        assert resp.status_code == 400
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify POST /todos/:id/tasksof handles extra fields appropriately."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.post(f"/todos/{todo}/tasksof", json={"id": project, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields (201) or reject them (400)
        assert resp.status_code in [200, 201, 400]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify POST /todos/:id/tasksof handles invalid data types."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.post(f"/todos/{todo}/tasksof", json={"id": 12345})
        # Should handle gracefully with 400 or might auto-convert
        assert resp.status_code in [200, 201, 400, 404]
