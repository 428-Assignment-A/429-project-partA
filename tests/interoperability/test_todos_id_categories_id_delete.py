"""
test_todos_id_categories_id_delete.py - Tests for DELETE /todos/:id/categories/:id endpoint

Documented behavior:
  - Deletes the relationship between a todo and a category
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent todo (404)
5. Delete with non-existent category (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on todo or category data
"""

import pytest


class TestTodosIdCategoriesIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /todos/:id/categories/:id deletes relationship."""
        # Create todo, category, and relationship
        todo = api.post("/todos", json={"title": "TodoDelRel"}).json()["id"]
        category = api.post("/categories", json={"title": "CatDelRel"}).json()["id"]
        api.post(f"/todos/{todo}/categories", json={"id": category})
        
        # Delete relationship
        resp = api.delete(f"/todos/{todo}/categories/{category}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /todos/:id/categories should not return deleted category."""
        # Create todo, category, and relationship
        todo = api.post("/todos", json={"title": "TodoCheckGone"}).json()["id"]
        category = api.post("/categories", json={"title": "CatCheckGone"}).json()["id"]
        api.post(f"/todos/{todo}/categories", json={"id": category})
        
        # Delete relationship
        api.delete(f"/todos/{todo}/categories/{category}")
        
        # Verify category not in list
        resp = api.get(f"/todos/{todo}/categories")
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert category not in category_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create todo and category but NO relationship
        todo = api.post("/todos", json={"title": "TodoNoRel"}).json()["id"]
        category = api.post("/categories", json={"title": "CatNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/todos/{todo}/categories/{category}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_todo_returns_404(self, api):
        """Verify DELETE returns 404 for unknown todo."""
        category = api.post("/categories", json={"title": "ValidCat"}).json()["id"]
        
        resp = api.delete(f"/todos/999999/categories/{category}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_category_returns_404(self, api):
        """Verify DELETE returns 404 for unknown category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.delete(f"/todos/{todo}/categories/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create todo, category, and relationship
        todo = api.post("/todos", json={"title": "TodoDelTwice"}).json()["id"]
        category = api.post("/categories", json={"title": "CatDelTwice"}).json()["id"]
        api.post(f"/todos/{todo}/categories", json={"id": category})
        
        # First delete
        first = api.delete(f"/todos/{todo}/categories/{category}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/todos/{todo}/categories/{category}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete todo or category."""
        # Create todo, category, and relationship
        todo = api.post("/todos", json={"title": "TodoStaysAlive", "description": "Keep me"}).json()
        category = api.post("/categories", json={"title": "CatStaysAlive", "description": "Keep me too"}).json()
        
        todo_id = todo["id"]
        category_id = category["id"]
        
        api.post(f"/todos/{todo_id}/categories", json={"id": category_id})
        
        # Delete relationship
        api.delete(f"/todos/{todo_id}/categories/{category_id}")
        
        # Verify todo and category still exist
        todo_resp = api.get(f"/todos/{todo_id}")
        category_resp = api.get(f"/categories/{category_id}")
        
        assert todo_resp.status_code == 200
        assert category_resp.status_code == 200
        
        # Verify their data is unchanged
        assert todo_resp.json()["todos"][0]["title"] == "TodoStaysAlive"
        assert category_resp.json()["categories"][0]["title"] == "CatStaysAlive"
