"""
test_projects_id_tasks_get.py - Tests for GET /projects/:id/tasks endpoint

Documented behavior:
  - Returns all todo items related to project by the relationship named 'tasks'
  - Expected: 200 OK
  
Tests:
1. Get tasks for project with relationships (200)
2. Get tasks for project with no relationships (200, empty list)
3. Get tasks for non-existent project (404) - BUG
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestProjectsIdTasksGet:
    
    @pytest.mark.capability
    def test_get_tasks_for_project_with_relationships(self, api):
        """Verify GET /projects/:id/tasks returns linked todos."""
        # Create project and todos
        project = api.post("/projects", json={"title": "ProjectWithTasks"}).json()["id"]
        task1 = api.post("/todos", json={"title": "Task1"}).json()["id"]
        task2 = api.post("/todos", json={"title": "Task2"}).json()["id"]
        
        # Link todos to project
        api.post(f"/projects/{project}/tasks", json={"id": task1})
        api.post(f"/projects/{project}/tasks", json={"id": task2})
        
        # Get tasks
        resp = api.get(f"/projects/{project}/tasks")
        assert resp.status_code == 200
        
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert task1 in todo_ids
        assert task2 in todo_ids
    
    @pytest.mark.capability
    def test_get_tasks_for_project_without_relationships(self, api):
        """Verify GET /projects/:id/tasks returns empty list for project with no tasks."""
        project = api.post("/projects", json={"title": "ProjectNoTasks"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/tasks")
        assert resp.status_code == 200
        
        todos = resp.json().get("todos", [])
        assert len(todos) == 0
    
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: GET endpoint returns 200 OK instead of 404 for non-existent project ID")
    @pytest.mark.error
    def test_get_tasks_nonexistent_project_returns_404(self, api):
        """Verify GET /projects/:id/tasks returns 404 for unknown project.
        
        Expected: 404 Not Found
        Actual: 200 OK with empty list
        """
        resp = api.get("/projects/999999/tasks")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /projects/:id/tasks returns JSON by default."""
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/tasks", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /projects/:id/tasks can return XML."""
        project = api.post("/projects", json={"title": "XMLProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/tasks", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /projects/:id/tasks doesn't modify data."""
        # Create project with task
        project = api.post("/projects", json={"title": "NoSideEffectProject"}).json()["id"]
        task = api.post("/todos", json={"title": "NoSideEffectTask"}).json()["id"]
        api.post(f"/projects/{project}/tasks", json={"id": task})
        
        # Get initial state
        initial = api.get(f"/projects/{project}/tasks").json()
        
        # Perform GET again
        api.get(f"/projects/{project}/tasks")
        
        # Verify state unchanged
        after = api.get(f"/projects/{project}/tasks").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /projects/:id/tasks returns 200 for valid request."""
        project = api.post("/projects", json={"title": "StatusCodeProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/tasks")
        assert resp.status_code == 200
