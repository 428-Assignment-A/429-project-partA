"""
test_projects_id_categories_post.py - Tests for POST /projects/:id/categories endpoint

Documented behavior:
  - Creates a relationship named 'categories' between a project and a category
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid project and category (201)
2. Verify relationship exists after creation
3. Create relationship with non-existent project (404)
4. Create relationship with non-existent category (404)
5. Create duplicate relationship (should succeed)
6. Verify JSON response format
7. Verify no side effects on project or category data
"""

import pytest


class TestProjectsIdCategoriesPost:
    
    @pytest.mark.capability
    def test_create_relationship_valid_project_category_returns_201(self, api):
        """Verify POST /projects/:id/categories creates relationship."""
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/categories", json={"id": category})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /projects/:id/categories should return the category."""
        project = api.post("/projects", json={"title": "VerifyProject"}).json()["id"]
        category = api.post("/categories", json={"title": "VerifyCategory"}).json()["id"]
        
        api.post(f"/projects/{project}/categories", json={"id": category})
        
        resp = api.get(f"/projects/{project}/categories")
        assert resp.status_code == 200
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert category in category_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_project_returns_404(self, api):
        """Verify POST /projects/:id/categories returns 404 for unknown project."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.post("/projects/999999/categories", json={"id": category})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_category_returns_404(self, api):
        """Verify POST /projects/:id/categories returns 404 for unknown category."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/categories", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same categories relationship twice should not fail."""
        project = api.post("/projects", json={"title": "DupProject"}).json()["id"]
        category = api.post("/categories", json={"title": "DupCategory"}).json()["id"]
        
        first = api.post(f"/projects/{project}/categories", json={"id": category})
        assert first.status_code == 201
        
        second = api.post(f"/projects/{project}/categories", json={"id": category})
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /projects/:id/categories returns JSON response."""
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        
        resp = api.post(f"/projects/{project}/categories", json={"id": category})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_entities(self, api):
        """Creating relationship should not modify project or category data."""
        project_data = {"title": "OriginalProject", "description": "Keep this"}
        category_data = {"title": "OriginalCategory", "description": "Keep this too"}
        
        project = api.post("/projects", json=project_data).json()
        category = api.post("/categories", json=category_data).json()
        
        project_id = project["id"]
        category_id = category["id"]
        
        # Get original state
        original_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        original_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        
        # Create relationship
        api.post(f"/projects/{project_id}/categories", json={"id": category_id})
        
        # Verify data unchanged
        after_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        after_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        
        assert original_project["title"] == after_project["title"]
        assert original_category["title"] == after_category["title"]
