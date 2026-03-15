"""
test_projects_id_tasks_post.py - Tests for POST /projects/:id/tasks endpoint

Documented behavior:
  - Creates a relationship named 'tasks' between a project and a todo
  - Todo becomes a task of the project
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid project and todo (201)
2. Verify relationship exists after creation
3. Create relationship with non-existent project (404)
4. Create relationship with non-existent todo (404)
5. Create duplicate relationship (should succeed)
6. Verify JSON response format
7. Verify no side effects on project or todo data
8. Test malformed JSON - missing id field
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestProjectsIdTasksPost:
    
    @pytest.mark.capability
    def test_create_relationship_valid_project_todo_returns_201(self, api):
        """Verify POST /projects/:id/tasks creates relationship."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        todo = api.post("/todos", json={"title": "TestTask"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/tasks", json={"id": todo})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /projects/:id/tasks should return the todo."""
        project = api.post("/projects", json={"title": "VerifyProject"}).json()["id"]
        todo = api.post("/todos", json={"title": "VerifyTask"}).json()["id"]
        
        api.post(f"/projects/{project}/tasks", json={"id": todo})
        
        resp = api.get(f"/projects/{project}/tasks")
        assert resp.status_code == 200
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert todo in todo_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_project_returns_404(self, api):
        """Verify POST /projects/:id/tasks returns 404 for unknown project."""
        todo = api.post("/todos", json={"title": "ValidTask"}).json()["id"]
        
        resp = api.post("/projects/999999/tasks", json={"id": todo})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_todo_returns_404(self, api):
        """Verify POST /projects/:id/tasks returns 404 for unknown todo."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/tasks", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same tasks relationship twice should not fail."""
        project = api.post("/projects", json={"title": "DupProject"}).json()["id"]
        todo = api.post("/todos", json={"title": "DupTask"}).json()["id"]
        
        first = api.post(f"/projects/{project}/tasks", json={"id": todo})
        assert first.status_code == 201
        
        second = api.post(f"/projects/{project}/tasks", json={"id": todo})
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /projects/:id/tasks returns JSON response."""
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        todo = api.post("/todos", json={"title": "JSONTask"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/tasks", json={"id": todo})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_entities(self, api):
        """Creating relationship should not modify project or todo data."""
        project_data = {"title": "OriginalProject", "description": "Keep this"}
        todo_data = {"title": "OriginalTask", "description": "Keep this too"}
        
        project = api.post("/projects", json=project_data).json()
        todo = api.post("/todos", json=todo_data).json()
        
        project_id = project["id"]
        todo_id = todo["id"]
        
        # Get original state
        original_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        original_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        
        # Create relationship
        api.post(f"/projects/{project_id}/tasks", json={"id": todo_id})
        
        # Verify data unchanged
        after_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        after_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        
        assert original_project["title"] == after_project["title"]
        assert original_todo["title"] == after_todo["title"]
    
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify POST /projects/:id/tasks returns 400 when id field is missing."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.post(f"/projects/{project}/tasks", json={})
        assert resp.status_code == 400
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify POST /projects/:id/tasks handles extra fields appropriately."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        todo = api.post("/todos", json={"title": "TestTask"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.post(f"/projects/{project}/tasks", json={"id": todo, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields (201) or reject them (400)
        assert resp.status_code in [200, 201, 400]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify POST /projects/:id/tasks handles invalid data types."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.post(f"/projects/{project}/tasks", json={"id": 12345})
        # Should handle gracefully with 400 or might auto-convert
        assert resp.status_code in [200, 201, 400, 404]
