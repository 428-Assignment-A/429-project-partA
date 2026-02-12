"""
test_todos_id_tasksof_get.py - Tests for GET /todos/:id/tasksof endpoint

Documented behavior:
  - Returns all project items related to todo by the relationship named 'tasksof'
  - Expected: 200 OK
  
Tests:
1. Get projects for todo with relationships (200)
2. Get projects for todo with no relationships (200, empty list)
3. Get projects for non-existent todo (404)
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestTodosIdTasksofGet:
    
    @pytest.mark.capability
    def test_get_projects_for_todo_with_relationships(self, api):
        """Verify GET /todos/:id/tasksof returns linked projects."""
        # Create todo and projects
        todo = api.post("/todos", json={"title": "TodoWithProjects"}).json()["id"]
        proj1 = api.post("/projects", json={"title": "Project1"}).json()["id"]
        proj2 = api.post("/projects", json={"title": "Project2"}).json()["id"]
        
        # Link projects to todo
        api.post(f"/todos/{todo}/tasksof", json={"id": proj1})
        api.post(f"/todos/{todo}/tasksof", json={"id": proj2})
        
        # Get projects
        resp = api.get(f"/todos/{todo}/tasksof")
        assert resp.status_code == 200
        
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert proj1 in project_ids
        assert proj2 in project_ids
    
    @pytest.mark.capability
    def test_get_projects_for_todo_without_relationships(self, api):
        """Verify GET /todos/:id/tasksof returns empty list for todo with no projects."""
        todo = api.post("/todos", json={"title": "TodoNoProjects"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/tasksof")
        assert resp.status_code == 200
        
        projects = resp.json().get("projects", [])
        assert len(projects) == 0
    
    @pytest.mark.error
    def test_get_projects_nonexistent_todo_returns_404(self, api):
        """Verify GET /todos/:id/tasksof returns 404 for unknown todo."""
        resp = api.get("/todos/999999/tasksof")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /todos/:id/tasksof returns JSON by default."""
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/tasksof", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /todos/:id/tasksof can return XML."""
        todo = api.post("/todos", json={"title": "XMLTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/tasksof", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /todos/:id/tasksof doesn't modify data."""
        # Create todo with project
        todo = api.post("/todos", json={"title": "NoSideEffectTodo"}).json()["id"]
        project = api.post("/projects", json={"title": "NoSideEffectProj"}).json()["id"]
        api.post(f"/todos/{todo}/tasksof", json={"id": project})
        
        # Get initial state
        initial = api.get(f"/todos/{todo}/tasksof").json()
        
        # Perform GET again
        api.get(f"/todos/{todo}/tasksof")
        
        # Verify state unchanged
        after = api.get(f"/todos/{todo}/tasksof").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /todos/:id/tasksof returns 200 for valid request."""
        todo = api.post("/todos", json={"title": "StatusCodeTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/tasksof")
        assert resp.status_code == 200
