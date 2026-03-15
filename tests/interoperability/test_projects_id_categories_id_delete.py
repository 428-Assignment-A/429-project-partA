"""
test_projects_id_categories_id_delete.py - Tests for DELETE /projects/:id/categories/:id endpoint

Documented behavior:
  - Deletes the relationship between a project and a category
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent project (404)
5. Delete with non-existent category (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on project or category data
"""

import pytest


class TestProjectsIdCategoriesIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /projects/:id/categories/:id deletes relationship."""
        # Create project, category, and relationship
        project = api.post("/projects", json={"title": "ProjectDelRel"}).json()["id"]
        category = api.post("/categories", json={"title": "CatDelRel"}).json()["id"]
        api.post(f"/projects/{project}/categories", json={"id": category})
        
        # Delete relationship
        resp = api.delete(f"/projects/{project}/categories/{category}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /projects/:id/categories should not return deleted category."""
        # Create project, category, and relationship
        project = api.post("/projects", json={"title": "ProjectCheckGone"}).json()["id"]
        category = api.post("/categories", json={"title": "CatCheckGone"}).json()["id"]
        api.post(f"/projects/{project}/categories", json={"id": category})
        
        # Delete relationship
        api.delete(f"/projects/{project}/categories/{category}")
        
        # Verify category not in list
        resp = api.get(f"/projects/{project}/categories")
        categories = resp.json().get("categories", [])
        category_ids = [c["id"] for c in categories]
        assert category not in category_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create project and category but NO relationship
        project = api.post("/projects", json={"title": "ProjectNoRel"}).json()["id"]
        category = api.post("/categories", json={"title": "CatNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/projects/{project}/categories/{category}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_project_returns_404(self, api):
        """Verify DELETE returns 404 for unknown project."""
        category = api.post("/categories", json={"title": "ValidCat"}).json()["id"]
        
        resp = api.delete(f"/projects/999999/categories/{category}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_category_returns_404(self, api):
        """Verify DELETE returns 404 for unknown category."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.delete(f"/projects/{project}/categories/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create project, category, and relationship
        project = api.post("/projects", json={"title": "ProjectDelTwice"}).json()["id"]
        category = api.post("/categories", json={"title": "CatDelTwice"}).json()["id"]
        api.post(f"/projects/{project}/categories", json={"id": category})
        
        # First delete
        first = api.delete(f"/projects/{project}/categories/{category}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/projects/{project}/categories/{category}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete project or category."""
        # Create project, category, and relationship
        project = api.post("/projects", json={"title": "ProjectStaysAlive", "description": "Keep me"}).json()
        category = api.post("/categories", json={"title": "CatStaysAlive", "description": "Keep me too"}).json()
        
        project_id = project["id"]
        category_id = category["id"]
        
        api.post(f"/projects/{project_id}/categories", json={"id": category_id})
        
        # Delete relationship
        api.delete(f"/projects/{project_id}/categories/{category_id}")
        
        # Verify project and category still exist
        project_resp = api.get(f"/projects/{project_id}")
        category_resp = api.get(f"/categories/{category_id}")
        
        assert project_resp.status_code == 200
        assert category_resp.status_code == 200
        
        # Verify their data is unchanged
        assert project_resp.json()["projects"][0]["title"] == "ProjectStaysAlive"
        assert category_resp.json()["categories"][0]["title"] == "CatStaysAlive"
