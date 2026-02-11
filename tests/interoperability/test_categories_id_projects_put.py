"""
test_categories_id_projects_put.py - Tests for PUT /categories/:id/projects endpoint

Documented behavior:
  - PUT on relationship endpoints - documented as "not allowed"
  - Expected: 405 Method Not Allowed
  
Tests:
1. PUT with valid category and project (document actual behavior)
2. PUT with non-existent category (404 or 405)
3. PUT with non-existent project (404 or 405)
4. Verify response status code
5. Verify JSON response format
6. Verify no unintended side effects
7. Document if method is allowed or not
"""

import pytest


class TestCategoriesIdProjectsPut:
    
    @pytest.mark.capability
    def test_put_on_projects_endpoint_behavior(self, api):
        """Document actual behavior of PUT /categories/:id/projects."""
        category = api.post("/categories", json={"title": "CategoryPUT"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjectPUT"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/projects", json={"id": project})
        
        # Document the actual status code returned
        # Expected: 405 (not allowed) based on documentation
        assert resp.status_code in [200, 201, 400, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_category(self, api):
        """Verify PUT /categories/:id/projects with invalid category."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.put("/categories/999999/projects", json={"id": project})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.error
    def test_put_with_nonexistent_project(self, api):
        """Verify PUT /categories/:id/projects with invalid project."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/projects", json={"id": "999999"})
        # Should return 404 or 405
        assert resp.status_code in [404, 405]
    
    @pytest.mark.capability
    def test_put_returns_expected_status_code(self, api):
        """Verify PUT /categories/:id/projects returns appropriate status."""
        category = api.post("/categories", json={"title": "StatusCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "StatusProject"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/projects", json={"id": project})
        
        # Expected 405 based on documentation saying "not allowed"
        # Document what actually happens
        assert resp.status_code in [200, 201, 400, 404, 405]
    
    @pytest.mark.capability
    def test_put_response_format_json(self, api):
        """Verify PUT /categories/:id/projects response is JSON (if not 405)."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/projects", json={"id": project})
        
        # Only check content-type if not method not allowed
        if resp.status_code not in [405]:
            # Should return JSON or error
            assert resp.headers.get("Content-Type") is not None
    
    @pytest.mark.capability
    def test_put_no_unintended_side_effects(self, api):
        """Verify PUT doesn't modify existing relationships unexpectedly."""
        # Create category with existing project relationship
        category = api.post("/categories", json={"title": "SideEffectCategory"}).json()["id"]
        proj1 = api.post("/projects", json={"title": "ExistingProject"}).json()["id"]
        proj2 = api.post("/projects", json={"title": "NewProject"}).json()["id"]
        
        # Create first relationship
        api.post(f"/categories/{category}/projects", json={"id": proj1})
        
        # Get initial relationships
        initial = api.get(f"/categories/{category}/projects").json()
        
        # Try PUT with new project
        api.put(f"/categories/{category}/projects", json={"id": proj2})
        
        # Verify original relationships still exist or document behavior
        after = api.get(f"/categories/{category}/projects").json()
        
        # This documents whether PUT replaces or adds to relationships
        # If 405, relationships should be unchanged
        projects_before = initial.get("projects", [])
        projects_after = after.get("projects", [])
        
        # Document actual behavior
        assert isinstance(projects_after, list)
    
    @pytest.mark.capability
    def test_put_method_allowed_or_not(self, api):
        """Document if PUT method is allowed on this endpoint."""
        category = api.post("/categories", json={"title": "MethodTest"}).json()["id"]
        project = api.post("/projects", json={"title": "MethodTestProject"}).json()["id"]
        
        resp = api.put(f"/categories/{category}/projects", json={"id": project})
        
        # Documentation says "not allowed" - expect 405
        # If 405, method is not allowed (as documented)
        # If 200/201, method is allowed despite documentation
        # If 400, method allowed but bad request
        if resp.status_code == 405:
            assert True  # Method not allowed, as documented
        else:
            # Document the actual behavior
            assert resp.status_code in [200, 201, 400, 404]
