"""
test_categories_id_projects_get.py - Tests for GET /categories/:id/projects endpoint

Documented behavior:
  - Returns all project items related to category by the relationship named 'projects'
  - Expected: 200 OK
  
Tests:
1. Get projects for category with relationships (200)
2. Get projects for category with no relationships (200, empty list)
3. Get projects for non-existent category (404) - BUG
4. Verify JSON response format
5. Verify XML response format
6. Verify no side effects (GET doesn't modify data)
7. Verify correct status code
"""

import pytest


class TestCategoriesIdProjectsGet:
    
    @pytest.mark.capability
    def test_get_projects_for_category_with_relationships(self, api):
        """Verify GET /categories/:id/projects returns linked projects."""
        # Create category and projects
        category = api.post("/categories", json={"title": "CategoryWithProjects"}).json()["id"]
        proj1 = api.post("/projects", json={"title": "Project1"}).json()["id"]
        proj2 = api.post("/projects", json={"title": "Project2"}).json()["id"]
        
        # Link projects to category
        api.post(f"/categories/{category}/projects", json={"id": proj1})
        api.post(f"/categories/{category}/projects", json={"id": proj2})
        
        # Get projects
        resp = api.get(f"/categories/{category}/projects")
        assert resp.status_code == 200
        
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert proj1 in project_ids
        assert proj2 in project_ids
    
    @pytest.mark.capability
    def test_get_projects_for_category_without_relationships(self, api):
        """Verify GET /categories/:id/projects returns empty list for category with no projects."""
        category = api.post("/categories", json={"title": "CategoryNoProjects"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/projects")
        assert resp.status_code == 200
        
        projects = resp.json().get("projects", [])
        assert len(projects) == 0
    
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: GET endpoint returns 200 OK instead of 404 for non-existent category ID")
    @pytest.mark.error
    def test_get_projects_nonexistent_category_returns_404(self, api):
        """Verify GET /categories/:id/projects returns 404 for unknown category.
        
        Expected: 404 Not Found
        Actual: 200 OK with empty list
        """
        resp = api.get("/categories/999999/projects")
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_response_format_json(self, api):
        """Verify GET /categories/:id/projects returns JSON by default."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/projects", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_response_format_xml(self, api):
        """Verify GET /categories/:id/projects can return XML."""
        category = api.post("/categories", json={"title": "XMLCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/projects", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "xml" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_get_no_side_effects(self, api):
        """Verify GET /categories/:id/projects doesn't modify data."""
        # Create category with project
        category = api.post("/categories", json={"title": "NoSideEffectCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "NoSideEffectProj"}).json()["id"]
        api.post(f"/categories/{category}/projects", json={"id": project})
        
        # Get initial state
        initial = api.get(f"/categories/{category}/projects").json()
        
        # Perform GET again
        api.get(f"/categories/{category}/projects")
        
        # Verify state unchanged
        after = api.get(f"/categories/{category}/projects").json()
        assert initial == after
    
    @pytest.mark.capability
    def test_get_returns_correct_status_code(self, api):
        """Verify GET /categories/:id/projects returns 200 for valid request."""
        category = api.post("/categories", json={"title": "StatusCodeCategory"}).json()["id"]
        
        resp = api.get(f"/categories/{category}/projects")
        assert resp.status_code == 200
