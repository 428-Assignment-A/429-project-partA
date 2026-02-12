"""
test_projects_id_tasks_id_delete.py - Tests for DELETE /projects/:id/tasks/:id endpoint

Documented behavior:
  - Deletes the relationship between a project and a todo (task)
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent project (404)
5. Delete with non-existent todo (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on project or todo data
"""

import pytest


class TestProjectsIdTasksIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /projects/:id/tasks/:id deletes relationship."""
        # Create project, todo, and relationship
        project = api.post("/projects", json={"title": "ProjectDelRel"}).json()["id"]
        task = api.post("/todos", json={"title": "TaskDelRel"}).json()["id"]
        api.post(f"/projects/{project}/tasks", json={"id": task})
        
        # Delete relationship
        resp = api.delete(f"/projects/{project}/tasks/{task}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /projects/:id/tasks should not return deleted todo."""
        # Create project, todo, and relationship
        project = api.post("/projects", json={"title": "ProjectCheckGone"}).json()["id"]
        task = api.post("/todos", json={"title": "TaskCheckGone"}).json()["id"]
        api.post(f"/projects/{project}/tasks", json={"id": task})
        
        # Delete relationship
        api.delete(f"/projects/{project}/tasks/{task}")
        
        # Verify task not in list
        resp = api.get(f"/projects/{project}/tasks")
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert task not in todo_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create project and todo but NO relationship
        project = api.post("/projects", json={"title": "ProjectNoRel"}).json()["id"]
        task = api.post("/todos", json={"title": "TaskNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/projects/{project}/tasks/{task}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_project_returns_404(self, api):
        """Verify DELETE returns 404 for unknown project."""
        task = api.post("/todos", json={"title": "ValidTask"}).json()["id"]
        
        resp = api.delete(f"/projects/999999/tasks/{task}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_todo_returns_404(self, api):
        """Verify DELETE returns 404 for unknown todo."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.delete(f"/projects/{project}/tasks/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create project, todo, and relationship
        project = api.post("/projects", json={"title": "ProjectDelTwice"}).json()["id"]
        task = api.post("/todos", json={"title": "TaskDelTwice"}).json()["id"]
        api.post(f"/projects/{project}/tasks", json={"id": task})
        
        # First delete
        first = api.delete(f"/projects/{project}/tasks/{task}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/projects/{project}/tasks/{task}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete project or todo."""
        # Create project, todo, and relationship
        project = api.post("/projects", json={"title": "ProjectStaysAlive", "description": "Keep me"}).json()
        task = api.post("/todos", json={"title": "TaskStaysAlive", "description": "Keep me too"}).json()
        
        project_id = project["id"]
        task_id = task["id"]
        
        api.post(f"/projects/{project_id}/tasks", json={"id": task_id})
        
        # Delete relationship
        api.delete(f"/projects/{project_id}/tasks/{task_id}")
        
        # Verify project and todo still exist
        project_resp = api.get(f"/projects/{project_id}")
        task_resp = api.get(f"/todos/{task_id}")
        
        assert project_resp.status_code == 200
        assert task_resp.status_code == 200
        
        # Verify their data is unchanged
        assert project_resp.json()["projects"][0]["title"] == "ProjectStaysAlive"
        assert task_resp.json()["todos"][0]["title"] == "TaskStaysAlive"
