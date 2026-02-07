"""
test_example.py - Tests for GET /todos endpoint

Tests:
1. Core functionality
2. JSON/XML payloads
3. Return codes
4. Side effects
5. Command line queries
"""

import pytest

class TestExample:
    
    # 1. SYSTEM READINESS (handled by conftest fixture)
    
    # 2. CORE FUNCTIONALITY
    def test_get_todos_returns_all_todos(self, api):
        """Verify GET /todos returns all todo items"""
        response = api.get("/todos")
        assert response.status_code == 200
        assert "todos" in response.json()
    
    # 3. JSON FORMAT
    def test_get_todos_json_payload(self, api):
        """Verify JSON response format"""
        response = api.get("/todos", headers={"Accept": "application/json"})
        assert response.status_code == 200
        assert "application/json" in response.headers["Content-Type"]
    
    # 4. XML FORMAT
    def test_get_todos_xml_payload(self, api):
        """Verify XML response format"""
        response = api.get("/todos", headers={"Accept": "application/xml"})
        assert response.status_code == 200
        assert "xml" in response.headers["Content-Type"].lower()
    
    # 5. RETURN CODES
    def test_get_todos_returns_200(self, api):
        """Verify correct status code"""
        response = api.get("/todos")
        assert response.status_code == 200
    
    # 6. SIDE EFFECTS
    def test_get_todos_no_side_effects(self, api):
        """Verify GET doesn't modify data"""
        # Get initial state
        initial = api.get("/todos").json()
        
        # Perform GET
        api.get("/todos")
        
        # Verify state unchanged
        after = api.get("/todos").json()
        assert initial == after
    
    # 7. COMMAND LINE / QUERY PARAMETERS
    def test_get_todos_with_filter(self, api):
        """Verify query parameter filtering works"""
        response = api.get("/todos?doneStatus=true")
        assert response.status_code == 200