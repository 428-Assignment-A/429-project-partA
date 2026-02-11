"""
test_todos_id_tasksof_id_delete.py - Tests for DELETE /todos/:id/tasksof/:id endpoint

Documented behavior:
  - Deletes the relationship between a todo and a project
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent todo (404)
5. Delete with non-existent project (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on todo or project data
"""

import pytest


class TestTodosIdTasksofIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /todos/:id/tasksof/:id deletes relationship."""
        # Create todo, project, and relationship
        todo = api.post("/todos", json={"title": "TodoDelRel"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjDelRel"}).json()["id"]
        api.post(f"/todos/{todo}/tasksof", json={"id": project})
        
        # Delete relationship
        resp = api.delete(f"/todos/{todo}/tasksof/{project}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /todos/:id/tasksof should not return deleted project."""
        # Create todo, project, and relationship
        todo = api.post("/todos", json={"title": "TodoCheckGone"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjCheckGone"}).json()["id"]
        api.post(f"/todos/{todo}/tasksof", json={"id": project})
        
        # Delete relationship
        api.delete(f"/todos/{todo}/tasksof/{project}")
        
        # Verify project not in list
        resp = api.get(f"/todos/{todo}/tasksof")
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert project not in project_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create todo and project but NO relationship
        todo = api.post("/todos", json={"title": "TodoNoRel"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/todos/{todo}/tasksof/{project}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_todo_returns_404(self, api):
        """Verify DELETE returns 404 for unknown todo."""
        project = api.post("/projects", json={"title": "ValidProj"}).json()["id"]
        
        resp = api.delete(f"/todos/999999/tasksof/{project}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_project_returns_404(self, api):
        """Verify DELETE returns 404 for unknown project."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.delete(f"/todos/{todo}/tasksof/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create todo, project, and relationship
        todo = api.post("/todos", json={"title": "TodoDelTwice"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjDelTwice"}).json()["id"]
        api.post(f"/todos/{todo}/tasksof", json={"id": project})
        
        # First delete
        first = api.delete(f"/todos/{todo}/tasksof/{project}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/todos/{todo}/tasksof/{project}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete todo or project."""
        # Create todo, project, and relationship
        todo = api.post("/todos", json={"title": "TodoStaysAlive", "description": "Keep me"}).json()
        project = api.post("/projects", json={"title": "ProjStaysAlive", "description": "Keep me too"}).json()
        
        todo_id = todo["id"]
        project_id = project["id"]
        
        api.post(f"/todos/{todo_id}/tasksof", json={"id": project_id})
        
        # Delete relationship
        api.delete(f"/todos/{todo_id}/tasksof/{project_id}")
        
        # Verify todo and project still exist
        todo_resp = api.get(f"/todos/{todo_id}")
        project_resp = api.get(f"/projects/{project_id}")
        
        assert todo_resp.status_code == 200
        assert project_resp.status_code == 200
        
        # Verify their data is unchanged
        assert todo_resp.json()["todos"][0]["title"] == "TodoStaysAlive"
        assert project_resp.json()["projects"][0]["title"] == "ProjStaysAlive"
