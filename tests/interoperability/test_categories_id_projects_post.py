"""
test_categories_id_projects_post.py - Tests for POST /categories/:id/projects endpoint

Documented behavior:
  - Creates a relationship named 'projects' between a category and a project
  - Expected: 201 Created
  
Tests:
1. Create relationship with valid category and project (201)
2. Verify relationship exists after creation
3. Create relationship with non-existent category (404)
4. Create relationship with non-existent project (404)
5. Create duplicate relationship (should succeed)
6. Verify JSON response format
7. Verify no side effects on category or project data
8. Test malformed JSON - missing id field - BUG
9. Test malformed JSON - extra random field
10. Test malformed JSON - invalid data type
"""

import pytest


class TestCategoriesIdProjectsPost:
    
    @pytest.mark.capability
    def test_create_relationship_valid_category_project_returns_201(self, api):
        """Verify POST /categories/:id/projects creates relationship."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/projects", json={"id": project})
        assert resp.status_code == 201
    
    @pytest.mark.capability
    def test_relationship_exists_after_creation(self, api):
        """After POST, GET /categories/:id/projects should return the project."""
        category = api.post("/categories", json={"title": "VerifyCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "VerifyProject"}).json()["id"]
        
        api.post(f"/categories/{category}/projects", json={"id": project})
        
        resp = api.get(f"/categories/{category}/projects")
        assert resp.status_code == 200
        projects = resp.json().get("projects", [])
        project_ids = [p["id"] for p in projects]
        assert project in project_ids
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_category_returns_404(self, api):
        """Verify POST /categories/:id/projects returns 404 for unknown category."""
        project = api.post("/projects", json={"title": "ValidProject"}).json()["id"]
        
        resp = api.post("/categories/999999/projects", json={"id": project})
        assert resp.status_code == 404
    
    @pytest.mark.error
    def test_create_relationship_nonexistent_project_returns_404(self, api):
        """Verify POST /categories/:id/projects returns 404 for unknown project."""
        category = api.post("/categories", json={"title": "ValidCategory"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/projects", json={"id": "999999"})
        assert resp.status_code == 404
    
    @pytest.mark.capability
    def test_create_duplicate_relationship_succeeds(self, api):
        """Creating the same projects relationship twice should not fail."""
        category = api.post("/categories", json={"title": "DupCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "DupProject"}).json()["id"]
        
        first = api.post(f"/categories/{category}/projects", json={"id": project})
        assert first.status_code == 201
        
        second = api.post(f"/categories/{category}/projects", json={"id": project})
        assert second.status_code in [200, 201]
    
    @pytest.mark.capability
    def test_response_format_is_json(self, api):
        """Verify POST /categories/:id/projects returns JSON response."""
        category = api.post("/categories", json={"title": "JSONCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "JSONProject"}).json()["id"]
        
        resp = api.post(f"/categories/{category}/projects", json={"id": project})
        assert "application/json" in resp.headers.get("Content-Type", "").lower()
    
    @pytest.mark.capability
    def test_no_side_effects_on_entities(self, api):
        """Creating relationship should not modify category or project data."""
        category_data = {"title": "OriginalCategory", "description": "Keep this"}
        project_data = {"title": "OriginalProject", "description": "Keep this too"}
        
        category = api.post("/categories", json=category_data).json()
        project = api.post("/projects", json=project_data).json()
        
        category_id = category["id"]
        project_id = project["id"]
        
        # Get original state
        original_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        original_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        
        # Create relationship
        api.post(f"/categories/{category_id}/projects", json={"id": project_id})
        
        # Verify data unchanged
        after_category = api.get(f"/categories/{category_id}").json()["categories"][0]
        after_project = api.get(f"/projects/{project_id}").json()["projects"][0]
        
        assert original_category["title"] == after_category["title"]
        assert original_project["title"] == after_project["title"]
    
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: API accepts empty body and returns 201 instead of 400")
    @pytest.mark.error
    def test_malformed_json_missing_id_field(self, api):
        """Verify POST /categories/:id/projects returns 400 when id field is missing.
        
        Expected: 400 Bad Request
        Actual: 201 Created (accepts empty body)
        """
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Missing required "id" field in body
        resp = api.post(f"/categories/{category}/projects", json={})
        assert resp.status_code == 400
    
    @pytest.mark.error
    def test_malformed_json_extra_random_field(self, api):
        """Verify POST /categories/:id/projects handles extra fields appropriately."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        project = api.post("/projects", json={"title": "TestProject"}).json()["id"]
        
        # Extra random field that's not in API specification
        resp = api.post(f"/categories/{category}/projects", json={"id": project, "randomField": "unexpected", "anotherField": 123})
        # API should either ignore extra fields (201) or reject them (400)
        assert resp.status_code in [200, 201, 400]
    
    @pytest.mark.error
    def test_malformed_json_invalid_data_type(self, api):
        """Verify POST /categories/:id/projects handles invalid data types."""
        category = api.post("/categories", json={"title": "TestCategory"}).json()["id"]
        
        # Invalid data type - sending number instead of string for id
        resp = api.post(f"/categories/{category}/projects", json={"id": 12345})
        # Should handle gracefully with 400 or might auto-convert
        assert resp.status_code in [200, 201, 400, 404]
```

---
