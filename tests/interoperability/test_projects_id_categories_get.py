"""
test_projects_id_categories_get.py - Tests for GET /projects/:id/categories endpoint

Documented behavior:
  - Returns all category items related to project by the relationship named 'categories'
  - Expected: 200 OK
  
Tests:
1. Get categories for project with relationships (200)
2. Get categories for project with no relationships (200, empty list)
3. Get categories for non-existent project (404)
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestProjectsIdCategoriesGet:
    
    @pytest.mark.capability
    def test_get_categories_for_project_with_relationships(self, api):
        """Verify GET /projects/:id/categories returns linked categories."""
        # Create project and categories
        project = api.post("/projects", json={"title": "ProjectWithCats"}).json()["id"]
        cat1 = api.post("/categories", json={"title": "Category1"}).json()["id"]
        cat2 = api.post("/categories", json={"title": "Category2"}).json()["id"]
        
        # Link categories to project
        api.post(f"/projects/{project}/categories", json={"id": cat1})
        api.post(f"/projects/{project}/categories", json={"id": cat2})
        
        # Get categories
        resp = api.get(f"/projects/{project}/categories")
        assert resp.status_code == 200
        
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert cat1 in category_ids
        assert cat2 in category_ids
    
    @pytest.mark.capability
    def test_get_categories_for_project_without_relationships(self, api):
        """Verify GET /projects/:id/categories returns empty list for project with no categories."""
        project = api.post("/projects", json={"title": "ProjectNoCats"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/categories")
        assert resp.status_code == 200
        
        categories = resp.json().get("categories", [])
        assert len(categories) == 0
    
    @pytest.mark.error
    def test_get_categories_nonexistent_project_returns_404(self, api):
        """Verify GET /projects/:id/categories returns 404 for unknown project."""
        resp = api.get("/projects/999999/categories")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /projects/:id/categories returns JSON by default."""
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/categories", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /projects/:id/categories can return XML."""
        project = api.post("/projects", json={"title": "XMLProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/categories", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /projects/:id/categories doesn't modify data."""
        # Create project with category
        project = api.post("/projects", json={"title": "NoSideEffectProject"}).json()["id"]
        category = api.post("/categories", json={"title": "NoSideEffectCat"}).json()["id"]
        api.post(f"/projects/{project}/categories", json={"id": category})
        
        # Get initial state
        initial = api.get(f"/projects/{project}/categories").json()
        
        # Perform GET again
        api.get(f"/projects/{project}/categories")
        
        # Verify state unchanged
        after = api.get(f"/projects/{project}/categories").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /projects/:id/categories returns 200 for valid request."""
        project = api.post("/projects", json={"title": "StatusCodeProject"}).json()["id"]
        
        resp = api.get(f"/projects/{project}/categories")
        assert resp.status_code == 200
