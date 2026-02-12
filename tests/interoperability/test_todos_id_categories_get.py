"""
test_todos_id_categories_get.py - Tests for GET /todos/:id/categories endpoint

Documented behavior:
  - Returns all categories related to a todo by the relationship named 'categories'
  - Expected: 200 OK
  
Tests:
1. Get categories for todo with relationships (200)
2. Get categories for todo with no relationships (200, empty list)
3. Get categories for non-existent todo (404)
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestTodosIdCategoriesGet:
    
    @pytest.mark.capability
    def test_get_categories_for_todo_with_relationships(self, api):
        """Verify GET /todos/:id/categories returns linked categories."""
        # Create todo and categories
        todo = api.post("/todos", json={"title": "TodoWithCats"}).json()["id"]
        cat1 = api.post("/categories", json={"title": "Category1"}).json()["id"]
        cat2 = api.post("/categories", json={"title": "Category2"}).json()["id"]
        
        # Link categories to todo
        api.post(f"/todos/{todo}/categories", json={"id": cat1})
        api.post(f"/todos/{todo}/categories", json={"id": cat2})
        
        # Get categories
        resp = api.get(f"/todos/{todo}/categories")
        assert resp.status_code == 200
        
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert cat1 in category_ids
        assert cat2 in category_ids
    
    @pytest.mark.capability
    def test_get_categories_for_todo_without_relationships(self, api):
        """Verify GET /todos/:id/categories returns empty list for todo with no categories."""
        todo = api.post("/todos", json={"title": "TodoNoCats"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/categories")
        assert resp.status_code == 200
        
        categories = resp.json().get("categories", [])
        assert len(categories) == 0
    
    @pytest.mark.error
    def test_get_categories_nonexistent_todo_returns_404(self, api):
        """Verify GET /todos/:id/categories returns 404 for unknown todo."""
        resp = api.get("/todos/999999/categories")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /todos/:id/categories returns JSON by default."""
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/categories", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /todos/:id/categories can return XML."""
        todo = api.post("/todos", json={"title": "XMLTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/categories", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /todos/:id/categories doesn't modify data."""
        # Create todo with category
        todo = api.post("/todos", json={"title": "NoSideEffectTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "NoSideEffectCat"}).json()["id"]
        api.post(f"/todos/{todo}/categories", json={"id": category})
        
        # Get initial state
        initial = api.get(f"/todos/{todo}/categories").json()
        
        # Perform GET again
        api.get(f"/todos/{todo}/categories")
        
        # Verify state unchanged
        after = api.get(f"/todos/{todo}/categories").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /todos/:id/categories returns 200 for valid request."""
        todo = api.post("/todos", json={"title": "StatusCodeTodo"}).json()["id"]
        
        resp = api.get(f"/todos/{todo}/categories")
        assert resp.status_code == 200
