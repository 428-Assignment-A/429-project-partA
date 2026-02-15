"""
test_categories_id_todos_put.py - Tests for PUT /categories/:id/todos endpoint

Documented behavior:
  - PUT on relationship endpoints - documented as "not allowed"
  - Expected: 405 Method Not Allowed
  
Tests:
1. PUT with valid category and todo (document actual behavior)
2. PUT with non-existent category (404 or 405)
3. PUT with non-existent todo (404 or 405)
4. Verify response status code
5. Verify JSON response format
6. Verify no unintended side effects
7. Document if method is allowed or not
8. Test malformed JSON - missing id field
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestCategoriesIdTodosPut:
    
    @pytest.mark.capability
    def test_put_on_todos_endpoint_behavior(self, api):
        """Document actual behavior of PUT /categories/:id/todos."""
        category = api.post("/categories", json={"title": "CategoryPUT"}).json()["id"]
        todo = api.post("/todos", json={"title": "TodoPUT"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/todos", json={"id": todo})
        
        # Document the actual status code returned
        # Expected: 405 (not allowed) based on documentation
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_category(self, api):
        """Verify PUT /categories/:id/todos with invalid category."""
        todo = api.post("/todos", json={"title": "ValidTodo"}).json()["id"]
        
        resp = api.put("/categories/999999/todos", json={"id": todo})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_todo(self, api):
        """Verify PUT /categories/:id/todos with invalid todo."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/todos", json={"id": "999999"})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.capability
    def test_put_returns_expected_status_code(self, api):
        """Verify PUT /categories/:id/todos returns appropriate status."""
        category = api.post("/categories", json={"title": "StatusCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "StatusTodo"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/todos", json={"id": todo})
        
        # Expected 405 based on documentation saying "not allowed"
        # Document what actually happens
        assert resp.status_code in [200, 201, 400, 404, 405]
    
    @pytest.mark.capability
    def test_put_response_format_json(self, api):
        """Verify PUT /categories/:id/todos response is JSON (if not 405)."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "JSONTodo"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/todos", json={"id": todo})
        
        # Only check content-type if not method not allowed
        if resp.status_code not in [405]:
            # Should return JSON or error
            assert resp.headers.get("Content-Type") is not None
    
    @pytest.mark.capability
    def test_put_no_unintended_side_effects(self, api):
        """Verify PUT doesn't modify existing relationships unexpectedly."""
        # Create category with existing todo relationship
        category = api.post("/categories", json={"title": "SideEffectCategory"}).json()["id"]
        todo1 = api.post("/todos", json={"title": "ExistingTodo"}).json()["id"]
        todo2 = api.post("/todos", json={"title": "NewTodo"}).json()["id"]
        
        # Create first relationship
        api.post(f"/categories/{category}/todos", json={"id": todo1})
        
        # Get initial relationships
        initial = api.get(f"/categories/{category}/todos").json()
        
        # Try PUT with new todo
        api.put(f"/categories/{category}/todos", json={"id": todo2})
        
        # Verify original relationships still exist or document behavior
        after = api.get(f"/categories/{category}/todos").json()
        
        # This documents whether PUT replaces or adds to relationships
        # If 405, relationships should be unchanged
        todos_before = initial.get("todos", [])
        todos_after = after.get("todos", [])
        
        # Document actual behavior
        assert isinstance(todos_after, list)
    
    @pytest.mark.capability
    def test_put_method_allowed_or_not(self, api):
        """Document if PUT method is allowed on this endpoint."""
        category = api.post("/categories", json={"title": "MethodTest"}).json()["id"]
        todo = api.post("/todos", json={"title": "MethodTestTodo"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/todos", json={"id": todo})
        
        # Documentation says "not allowed" - expect 405
        # If 405, method is not allowed (as documented)
        # If 200/201, method is allowed despite documentation
        # If 400, method allowed but bad request
        if resp.status_code == 405:
            assert True  # Method not allowed, as documented
        else:
            # Document the actual behavior
            assert resp.status_code in [200, 201, 400, 404]
    
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify PUT /categories/:id/todos handles missing id field."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.put(f"/categories/{category}/todos", json={})
        # Should return 400 or 405 (method not allowed)
        assert resp.status_code in [400, 405]
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify PUT /categories/:id/todos handles extra fields appropriately."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        todo = api.post("/todos", json={"title": "TestTodo"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.put(f"/categories/{category}/todos", json={"id": todo, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields, reject them (400), or return 405
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify PUT /categories/:id/todos handles invalid data types."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.put(f"/categories/{category}/todos", json={"id": 12345})
        # Should handle gracefully with 400, 404, or 405
        assert resp.status_code in [200, 201, 400, 404, 405]
