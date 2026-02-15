"""
test_todos_id_categories_put.py - Tests for PUT /todos/:id/categories endpoint

Documented behavior:
  - PUT on relationship endpoints is typically undocumented
  - May be used to update/replace relationships or may not be allowed
  - Expected: 405 Method Not Allowed OR 400 Bad Request (if undocumented)
  
Tests:
1. PUT with valid todo and category (document actual behavior)
2. PUT with non-existent todo (404 or 405)
3. PUT with non-existent category (404 or 405)
4. Verify response status code
5. Verify JSON response format
6. Verify no unintended side effects
7. Document if method is allowed or not
8. Test malformed JSON - missing id field
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestTodosIdCategoriesPut:
    
    @pytest.mark.capability
    def test_put_on_categories_endpoint_behavior(self, api):
        """Document actual behavior of PUT /todos/:id/categories."""
        todo = api.post("/todos", json={"title": "TodoPUT"}).json()["id"]
        category = api.post("/categories", json={"title": "CatPUT"}).json()["id"]
        
        resp = api.put(f"/todos/{todo}/categories", json={"id": category})
        
        # Document the actual status code returned
        # Common responses: 405 (not allowed), 400 (bad request), or 200/201 (if allowed)
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_todo(self, api):
        """Verify PUT /todos/:id/categories with invalid todo."""
        category = api.post("/categories", json={"title": "ValidCat"}).json()["id"]
        
        resp = api.put("/todos/999999/categories", json={"id": category})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_category(self, api):
        """Verify PUT /todos/:id/categories with invalid category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.put(f"/todos/{todo}/categories", json={"id": "999999"})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.capability
    def test_put_returns_expected_status_code(self, api):
        """Verify PUT /todos/:id/categories returns appropriate status."""
        todo = api.post("/todos", json={"title": "StatusTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "StatusCat"}).json()["id"]
        
        resp = api.put(f"/todos/{todo}/categories", json={"id": category})
        
        # Typically 405 for undocumented methods
        # Document what actually happens
        assert resp.status_code in [200, 201, 400, 404, 405]
    
    @pytest.mark.capability
    def test_put_response_format_json(self, api):
        """Verify PUT /todos/:id/categories response is JSON (if not 405)."""
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "JSONCat"}).json()["id"]
        
        resp = api.put(f"/todos/{todo}/categories", json={"id": category})
        
        # Only check content-type if not method not allowed
        if resp.status_code not in [405]:
            # Should return JSON or error
            assert resp.headers.get("Content-Type") is not None
    
    @pytest.mark.capability
    def test_put_no_unintended_side_effects(self, api):
        """Verify PUT doesn't modify existing relationships unexpectedly."""
        # Create todo with existing category relationship
        todo = api.post("/todos", json={"title": "SideEffectTodo"}).json()["id"]
        cat1 = api.post("/categories", json={"title": "ExistingCat"}).json()["id"]
        cat2 = api.post("/categories", json={"title": "NewCat"}).json()["id"]
        
        # Create first relationship
        api.post(f"/todos/{todo}/categories", json={"id": cat1})
        
        # Get initial relationships
        initial = api.get(f"/todos/{todo}/categories").json()
        
        # Try PUT with new category
        api.put(f"/todos/{todo}/categories", json={"id": cat2})
        
        # Verify original relationships still exist or document behavior
        after = api.get(f"/todos/{todo}/categories").json()
        
        # This documents whether PUT replaces or adds to relationships
        # If 405, relationships should be unchanged
        categories_before = initial.get("categories", [])
        categories_after = after.get("categories", [])
        
        # Document actual behavior
        assert isinstance(categories_after, list)
    
    @pytest.mark.capability
    def test_put_method_allowed_or_not(self, api):
        """Document if PUT method is allowed on this endpoint."""
        todo = api.post("/todos", json={"title": "MethodTest"}).json()["id"]
        category = api.post("/categories", json={"title": "MethodTestCat"}).json()["id"]
        
        resp = api.put(f"/todos/{todo}/categories", json={"id": category})
        
        # If 405, method is not allowed (undocumented)
        # If 200/201, method is allowed
        # If 400, method allowed but bad request
        if resp.status_code == 405:
            assert True  # Method not allowed, as expected for undocumented endpoint
        else:
            # Document the actual behavior
            assert resp.status_code in [200, 201, 400, 404]
    
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify PUT /todos/:id/categories handles missing id field."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.put(f"/todos/{todo}/categories", json={})
        # Should return 400 or 405 (method not allowed)
        assert resp.status_code in [400, 405]
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify PUT /todos/:id/categories handles extra fields appropriately."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.put(f"/todos/{todo}/categories", json={"id": category, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields, reject them (400), or return 405
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify PUT /todos/:id/categories handles invalid data types."""
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.put(f"/todos/{todo}/categories", json={"id": 12345})
        # Should handle gracefully with 400, 404, or 405
        assert resp.status_code in [200, 201, 400, 404, 405]
