"""
test_categories_id_projects_id_delete.py - Tests for DELETE /categories/:id/projects/:id endpoint

Documented behavior:
  - Deletes the relationship between a category and a project
  - Expected: 200 OK
  
Tests:
1. Delete existing relationship (200)
2. Verify relationship is gone after delete (GET doesn't return it)
3. Delete non-existent relationship (404)
4. Delete with non-existent category (404)
5. Delete with non-existent project (404)
6. Delete twice (second should fail with 404)
7. Verify no side effects on category or project data
"""

import pytest


class TestCategoriesIdProjectsIdDelete:
    
    @pytest.mark.capability
    def test_delete_existing_relationship_returns_200(self, api):
        """Verify DELETE /categories/:id/projects/:id deletes relationship."""
        # Create category, project, and relationship
        category = api.post("/categories", json={"title": "CategoryDelRel"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjectDelRel"}).json()["id"]
        api.post(f"/categories/{category}/projects", json={"id": project})
        
        # Delete relationship
        resp = api.delete(f"/categories/{category}/projects/{project}")
        assert resp.status_code == 200
    
    @pytest.mark.capability
    def test_relationship_gone_after_delete(self, api):
        """After DELETE, GET /categories/:id/projects should not return deleted project."""
        # Create category, project, and relationship
        category = api.post("/categories", json={"title": "CategoryCheckGone"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjectCheckGone"}).json()["id"]
        api.post(f"/categories/{category}/projects", json={"id": project})
        
        # Delete relationship
        api.delete(f"/categories/{category}/projects/{project}")
        
        # Verify project not in list
        resp = api.get(f"/categories/{category}/projects")
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert project not in project_ids
    
    @pytest.mark.error
    def test_delete_nonexistent_relationship_returns_404(self, api):
        """Verify DELETE returns 404 for relationship that doesn't exist."""
        # Create category and project but NO relationship
        category = api.post("/categories", json={"title": "CategoryNoRel"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjectNoRel"}).json()["id"]
        
        # Try to delete non-existent relationship
        resp = api.delete(f"/categories/{category}/projects/{project}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_category_returns_404(self, api):
        """Verify DELETE returns 404 for unknown category."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.delete(f"/categories/999999/projects/{project}")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_with_nonexistent_project_returns_404(self, api):
        """Verify DELETE returns 404 for unknown project."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.delete(f"/categories/{category}/projects/999999")
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_delete_same_relationship_twice_second_fails(self, api):
        """Second DELETE of same relationship should return 404."""
        # Create category, project, and relationship
        category = api.post("/categories", json={"title": "CategoryDelTwice"}).json()["id"]
        project = api.post("/projects", json={"title": "ProjectDelTwice"}).json()["id"]
        api.post(f"/categories/{category}/projects", json={"id": project})
        
        # First delete
        first = api.delete(f"/categories/{category}/projects/{project}")
        assert first.status_code == 200
        
        # Second delete
        second = api.delete(f"/categories/{category}/projects/{project}")
        assert second.status_code == 404
    
    @pytest.mark.capability
    def test_delete_relationship_no_side_effects_on_entities(self, api):
        """Deleting relationship should not delete category or project."""
        # Create category, project, and relationship
        category = api.post("/categories", json={"title": "CategoryStaysAlive", "description": "Keep me"}).json()
        project = api.post("/projects", json={"title": "ProjectStaysAlive", "description": "Keep me too"}).json()
        
        category_id = category["id"]
        project_id = project["id"]
        
        api.post(f"/categories/{category_id}/projects", json={"id": project_id})
        
        # Delete relationship
        api.delete(f"/categories/{category_id}/projects/{project_id}")
        
        # Verify category and project still exist
        category_resp = api.get(f"/categories/{category_id}")
        project_resp = api.get(f"/projects/{project_id}")
        
        assert category_resp.status_code == 200
        assert project_resp.status_code == 200
        
        # Verify their data is unchanged
        assert category_resp.json()["categories"][0]["title"] == "CategoryStaysAlive"
        assert project_resp.json()["projects"][0]["title"] == "ProjectStaysAlive"
