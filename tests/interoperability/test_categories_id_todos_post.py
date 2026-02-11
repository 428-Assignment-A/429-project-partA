"""
test_categories_id_todos_post.py - Tests for POST /categories/:id/todos endpoint

Documented behavior:
  - Creates a relationship named 'todos' between a category and a todo
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid category and todo (201)
2. Verify relationship exists after creation
3. Create relationship with non-existent category (404)
4. Create relationship with non-existent todo (404)
5. Create duplicate relationship (should succeed)
6. Verify JSON response format
7. Verify no side effects on category or todo data
"""

import pytest


class TestCategoriesIdTodosPost:
    
    @pytest.mark.capability
    def test_create_relationship_valid_category_todo_returns_201(self, api):
        """Verify POST /categories/:id/todos creates relationship."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/todos", json={"id": todo})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /categories/:id/todos should return the todo."""
        category = api.post("/categories", json={"title": "VerifyCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "VerifyTodo"}).json()["id"]
        
        api.post(f"/categories/{category}/todos", json={"id": todo})
        
        resp = api.get(f"/categories/{category}/todos")
        assert resp.status_code == 200
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert todo in todo_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_category_returns_404(self, api):
        """Verify POST /categories/:id/todos returns 404 for unknown category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.post("/categories/999999/todos", json={"id": todo})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_todo_returns_404(self, api):
        """Verify POST /categories/:id/todos returns 404 for unknown todo."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/todos", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same todos relationship twice should not fail."""
        category = api.post("/categories", json={"title": "DupCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "DupTodo"}).json()["id"]
        
        first = api.post(f"/categories/{category}/todos", json={"id": todo})
        assert first.status_code == 201
        
        second = api.post(f"/categories/{category}/todos", json={"id": todo})
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /categories/:id/todos returns JSON response."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/todos", json={"id": todo})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_entities(self, api):
        """Creating relationship should not modify category or todo data."""
        category_data = {"title": "OriginalCategory", "description": "Keep this"}
        todo_data = {"title": "OriginalTodo", "description": "Keep this too"}
        
        category = api.post("/categories", json=category_data).json()
        todo = api.post("/todos", json=todo_data).json()
        
        category_id = category["id"]
        todo_id = todo["id"]
        
        # Get original state
        original_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        original_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        
        # Create relationship
        api.post(f"/categories/{category_id}/todos", json={"id": todo_id})
        
        # Verify data unchanged
        after_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        after_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        
        assert original_category["title"] == after_category["title"]
        assert original_todo["title"] == after_todo["title"]
