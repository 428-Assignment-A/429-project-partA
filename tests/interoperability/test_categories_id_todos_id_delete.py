"""
test_categories_id_todos_id_delete.py - Tests for DELETE /categories/:id/todos/:id endpoint

Documented behavior:
  - Deletes the relationship between a category and a todo
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent category (404)
5. Delete with non-existent todo (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on category or todo data
"""

import pytest


class TestCategoriesIdTodosIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /categories/:id/todos/:id deletes relationship."""
        # Create category, todo, and relationship
        category = api.post("/categories", json={"title": "CategoryDelRel"}).json()["id"]
        todo = api.post("/todos", json={"title": "TodoDelRel"}).json()["id"]
        api.post(f"/categories/{category}/todos", json={"id": todo})
        
        # Delete relationship
        resp = api.delete(f"/categories/{category}/todos/{todo}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /categories/:id/todos should not return deleted todo."""
        # Create category, todo, and relationship
        category = api.post("/categories", json={"title": "CategoryCheckGone"}).json()["id"]
        todo = api.post("/todos", json={"title": "TodoCheckGone"}).json()["id"]
        api.post(f"/categories/{category}/todos", json={"id": todo})
        
        # Delete relationship
        api.delete(f"/categories/{category}/todos/{todo}")
        
        # Verify todo not in list
        resp = api.get(f"/categories/{category}/todos")
        todos = resp.json().get("todos", [])
        todo_ids = [t["id"] for t in todos]
        assert todo not in todo_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create category and todo but NO relationship
        category = api.post("/categories", json={"title": "CategoryNoRel"}).json()["id"]
        todo = api.post("/todos", json={"title": "TodoNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/categories/{category}/todos/{todo}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_category_returns_404(self, api):
        """Verify DELETE returns 404 for unknown category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.delete(f"/categories/999999/todos/{todo}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_todo_returns_404(self, api):
        """Verify DELETE returns 404 for unknown todo."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.delete(f"/categories/{category}/todos/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create category, todo, and relationship
        category = api.post("/categories", json={"title": "CategoryDelTwice"}).json()["id"]
        todo = api.post("/todos", json={"title": "TodoDelTwice"}).json()["id"]
        api.post(f"/categories/{category}/todos", json={"id": todo})
        
        # First delete
        first = api.delete(f"/categories/{category}/todos/{todo}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/categories/{category}/todos/{todo}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete category or todo."""
        # Create category, todo, and relationship
        category = api.post("/categories", json={"title": "CategoryStaysAlive", "description": "Keep me"}).json()
        todo = api.post("/todos", json={"title": "TodoStaysAlive", "description": "Keep me too"}).json()
        
        category_id = category["id"]
        todo_id = todo["id"]
        
        api.post(f"/categories/{category_id}/todos", json={"id": todo_id})
        
        # Delete relationship
        api.delete(f"/categories/{category_id}/todos/{todo_id}")
        
        # Verify category and todo still exist
        category_resp = api.get(f"/categories/{category_id}")
        todo_resp = api.get(f"/todos/{todo_id}")
        
        assert category_resp.status_code == 200
        assert todo_resp.status_code == 200
        
        # Verify their data is unchanged
        assert category_resp.json()["categories"][0]["title"] == "CategoryStaysAlive"
        assert todo_resp.json()["todos"][0]["title"] == "TodoStaysAlive"
