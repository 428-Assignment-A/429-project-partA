"""
test_categories_id_todos_get.py - Tests for GET /categories/:id/todos endpoint

Documented behavior:
  - Returns all todo items related to category by the relationship named 'todos'
  - Expected: 200 OK
  
Tests:
1. Get todos for category with relationships (200)
2. Get todos for category with no relationships (200, empty list)
3. Get todos for non-existent category (404)
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestCategoriesIdTodosGet:
    
    @pytest.mark.capability
    def test_get_todos_for_category_with_relationships(self, api):
        """Verify GET /categories/:id/todos returns linked todos."""
        # Create category and todos
        category = api.post("/categories", json={"title": "CategoryWithTodos"}).json()["id"]
        todo1 = api.post("/todos", json={"title": "Todo1"}).json()["id"]
        todo2 = api.post("/todos", json={"title": "Todo2"}).json()["id"]
        
        # Link todos to category
        api.post(f"/categories/{category}/todos", json={"id": todo1})
        api.post(f"/categories/{category}/todos", json={"id": todo2})
        
        # Get todos
        resp = api.get(f"/categories/{category}/todos")
        assert resp.status_code == 200
        
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert todo1 in todo_ids
        assert todo2 in todo_ids
    
    @pytest.mark.capability
    def test_get_todos_for_category_without_relationships(self, api):
        """Verify GET /categories/:id/todos returns empty list for category with no todos."""
        category = api.post("/categories", json={"title": "CategoryNoTodos"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/todos")
        assert resp.status_code == 200
        
        todos = resp.json().get("todos", [])
        assert len(todos) == 0
    
    @pytest.mark.error
    def test_get_todos_nonexistent_category_returns_404(self, api):
        """Verify GET /categories/:id/todos returns 404 for unknown category."""
        resp = api.get("/categories/999999/todos")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /categories/:id/todos returns JSON by default."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/todos", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /categories/:id/todos can return XML."""
        category = api.post("/categories", json={"title": "XMLCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/todos", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /categories/:id/todos doesn't modify data."""
        # Create category with todo
        category = api.post("/categories", json={"title": "NoSideEffectCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "NoSideEffectTodo"}).json()["id"]
        api.post(f"/categories/{category}/todos", json={"id": todo})
        
        # Get initial state
        initial = api.get(f"/categories/{category}/todos").json()
        
        # Perform GET again
        api.get(f"/categories/{category}/todos")
        
        # Verify state unchanged
        after = api.get(f"/categories/{category}/todos").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /categories/:id/todos returns 200 for valid request."""
        category = api.post("/categories", json={"title": "StatusCodeCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/todos")
        assert resp.status_code == 200
