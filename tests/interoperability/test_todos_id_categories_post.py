"""
test_todos_id_categories_post.py - Tests for POST /todos/:id/categories endpoint

Documented behavior:
  - Creates a relationship between a todo and a category
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid todo and category (201)
2. Verify relationship exists after creation (GET returns it)
3. Create relationship with non-existent todo (404)
4. Create relationship with non-existent category (404)
5. Create duplicate relationship (should succeed or return existing)
6. Verify JSON response format
7. Verify no side effects on todo or category data
8. Test malformed JSON - missing id field
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestTodosIdCategoriesPost:
    
    @pytest.mark.capability
    def test_create_relationship_valid_todo_category_returns_201(self, api):
        """Verify POST /todos/:id/categories creates relationship with valid IDs."""
        # Create a todo and category first
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Create relationship
        resp = api.post(f"/todos/{todo}/categories", json={"id": category})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /todos/:id/categories should return the category."""
        todo = api.post("/todos", json={"title": "TodoWithCat"}).json()["id"]
        category = api.post("/categories", json={"title": "CategoryForTodo"}).json()["id"]
        
        # Create relationship
        api.post(f"/todos/{todo}/categories", json={"id": category})
        
        # Verify relationship exists
        resp = api.get(f"/todos/{todo}/categories")
        assert resp.status_code == 200
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert category in category_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_todo_returns_404(self, api):
        """Verify POST /todos/:id/categories returns 404 for unknown todo."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.post("/todos/999999/categories", json={"id": category})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_category_returns_404(self, api):
        """Verify POST /todos/:id/categories returns 404 for unknown category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.post(f"/todos/{todo}/categories", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same relationship twice should not fail."""
        todo = api.post("/todos", json={"title": "DupRelTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "DupRelCat"}).json()["id"]
        
        # Create relationship first time
        first = api.post(f"/todos/{todo}/categories", json={"id": category})
        assert first.status_code == 201
        
        # Create relationship second time
        second = api.post(f"/todos/{todo}/categories", json={"id": category})
        # Should succeed or return 200/201
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /todos/:id/categories returns JSON response."""
        todo = api.post("/todos", json={"title": "JSONTestTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "JSONTestCat"}).json()["id"]
        
        resp = api.post(f"/todos/{todo}/categories", json={"id": category})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_todo_or_category(self, api):
        """Creating relationship should not modify todo or category data."""
        # Create todo and category with specific data
        todo_data = {"title": "SideEffectTodo", "description": "Original desc"}
        category_data = {"title": "SideEffectCat", "description": "Original cat desc"}
        
        todo = api.post("/todos", json=todo_data).json()
        category = api.post("/categories", json=category_data).json()
        
        todo_id = todo["id"]
        category_id = category["id"]
        
        # Get original state
        original_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        original_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        
        # Create relationship
        api.post(f"/todos/{todo_id}/categories", json={"id": category_id})
        
        # Verify todo and category data unchanged
        after_todo = api.get(f"/todos/{todo_id}").json()["todos"][0]
        after_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        
        assert original_todo["title"] == after_todo["title"]
        assert original_todo["description"] == after_todo["description"]
        assert original_category["title"] == after_category["title"]
        assert original_category["description"] == after_category["description"]
    
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify POST /todos/:id/categories returns 400 when id field is missing."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.post(f"/todos/{todo}/categories", json={})
        assert resp.status_code == 400
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify POST /todos/:id/categories handles extra fields appropriately."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.post(f"/todos/{todo}/categories", json={"id": category, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields (201) or reject them (400)
        assert resp.status_code in [200, 201, 400]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify POST /todos/:id/categories handles invalid data types."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.post(f"/todos/{todo}/categories", json={"id": 12345})
        # Should handle gracefully with 400 or might auto-convert
        assert resp.status_code in [200, 201, 400, 404]
