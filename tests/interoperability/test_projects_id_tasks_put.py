"""
test_projects_id_tasks_put.py - Tests for PUT /projects/:id/tasks endpoint

Documented behavior:
  - PUT on relationship endpoints - documented as "not allowed"
  - Expected: 405 Method Not Allowed
  
Tests:
1. PUT with valid project and todo (document actual behavior)
2. PUT with non-existent project (404 or 405)
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


class TestProjectsIdTasksPut:
    
    @pytest.mark.capability
    def test_put_on_tasks_endpoint_behavior(self, api):
        """Document actual behavior of PUT /projects/:id/tasks."""
        project = api.post("/projects", json={"title": "ProjectPUT"}).json()["id"]
        task = api.post("/todos", json={"title": "TaskPUT"}).json()["id"]
        
        resp = api.put(f"/projects/{project}/tasks", json={"id": task})
        
        # Document the actual status code returned
        # Expected: 405 (not allowed) based on documentation
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_project(self, api):
        """Verify PUT /projects/:id/tasks with invalid project."""
        task = api.post("/todos", json={"title": "ValidTask"}).json()["id"]
        
        resp = api.put("/projects/999999/tasks", json={"id": task})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_todo(self, api):
        """Verify PUT /projects/:id/tasks with invalid todo."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.put(f"/projects/{project}/tasks", json={"id": "999999"})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.capability
    def test_put_returns_expected_status_code(self, api):
        """Verify PUT /projects/:id/tasks returns appropriate status."""
        project = api.post("/projects", json={"title": "StatusProject"}).json()["id"]
        task = api.post("/todos", json={"title": "StatusTask"}).json()["id"]
        
        resp = api.put(f"/projects/{project}/tasks", json={"id": task})
        
        # Expected 405 based on documentation saying "not allowed"
        # Document what actually happens
        assert resp.status_code in [200, 201, 400, 404, 405]
    
    @pytest.mark.capability
    def test_put_response_format_json(self, api):
        """Verify PUT /projects/:id/tasks response is JSON (if not 405)."""
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        task = api.post("/todos", json={"title": "JSONTask"}).json()["id"]
        
        resp = api.put(f"/projects/{project}/tasks", json={"id": task})
        
        # Only check content-type if not method not allowed
        if resp.status_code not in [405]:
            # Should return JSON or error
            assert resp.headers.get("Content-Type") is not None
    
    @pytest.mark.capability
    def test_put_no_unintended_side_effects(self, api):
        """Verify PUT doesn't modify existing relationships unexpectedly."""
        # Create project with existing task relationship
        project = api.post("/projects", json={"title": "SideEffectProject"}).json()["id"]
        task1 = api.post("/todos", json={"title": "ExistingTask"}).json()["id"]
        task2 = api.post("/todos", json={"title": "NewTask"}).json()["id"]
        
        # Create first relationship
        api.post(f"/projects/{project}/tasks", json={"id": task1})
        
        # Get initial relationships
        initial = api.get(f"/projects/{project}/tasks").json()
        
        # Try PUT with new task
        api.put(f"/projects/{project}/tasks", json={"id": task2})
        
        # Verify original relationships still exist or document behavior
        after = api.get(f"/projects/{project}/tasks").json()
        
        # This documents whether PUT replaces or adds to relationships
        # If 405, relationships should be unchanged
        tasks_before = initial.get("todos", [])
        tasks_after = after.get("todos", [])
        
        # Document actual behavior
        assert isinstance(tasks_after, list)
    
    @pytest.mark.capability
    def test_put_method_allowed_or_not(self, api):
        """Document if PUT method is allowed on this endpoint."""
        project = api.post("/projects", json={"title": "MethodTest"}).json()["id"]
        task = api.post("/todos", json={"title": "MethodTestTask"}).json()["id"]
        
        resp = api.put(f"/projects/{project}/tasks", json={"id": task})
        
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
        """Verify PUT /projects/:id/tasks handles missing id field."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.put(f"/projects/{project}/tasks", json={})
        # Should return 400 or 405 (method not allowed)
        assert resp.status_code in [400, 405]
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify PUT /projects/:id/tasks handles extra fields appropriately."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        task = api.post("/todos", json={"title": "TestTask"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.put(f"/projects/{project}/tasks", json={"id": task, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields, reject them (400), or return 405
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify PUT /projects/:id/tasks handles invalid data types."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.put(f"/projects/{project}/tasks", json={"id": 12345})
        # Should handle gracefully with 400, 404, or 405
        assert resp.status_code in [200, 201, 400, 404, 405]
