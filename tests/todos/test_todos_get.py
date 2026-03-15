import pytest

class TestTodosGet:

    # 1. Capability: return all instances
    @pytest.mark.capability
    def test_get_all_todos_capability(self, api):
        """Confirm GET /todos returns the list of all todos."""
        resp = api.get("/todos")
        assert resp.status_code == 200
        assert "todos" in resp.json()
        assert isinstance(resp.json()["todos"], list)

    # 2. Capability: Observe specific data (Long Title)
    @pytest.mark.capability
    def test_get_todos_contains_long_title(self, api):
        """Verify the API can store and return the extreme long 'A' title from observations."""
        long_title = "A" * 500
        api.post("/todos", json={"title": long_title})
        
        resp = api.get("/todos")
        # Check if at least one todo has the long title
        titles = [t["title"] for t in resp.json()["todos"]]
        assert long_title in titles

    # 3. Capability: Observe specific data (XSS/Special Chars)
    @pytest.mark.capability
    def test_get_todos_contains_xss_chars(self, api):
        """Verify the API stores and returns XSS scripts and special characters."""
        xss_val = "<script>alert('xss')</script> & special chars: é, ñ, 中文"
        api.post("/todos", json={"title": xss_val})
        
        resp = api.get("/todos")
        titles = [t["title"] for t in resp.json()["todos"]]
        assert xss_val in titles

    # 4. Command Line Query: Filter by title
    @pytest.mark.capability
    def test_get_todos_filter_by_title(self, api):
        """Verify filtering via URL Query Parameters: /todos?title=..."""
        unique_title = "FilterMe123"
        api.post("/todos", json={"title": unique_title})
        
        # Test filtering
        resp = api.get(f"/todos?title={unique_title}")
        assert resp.status_code == 200
        for todo in resp.json()["todos"]:
            assert todo["title"] == unique_title

    # 5. Command Line Query: Filter by description
    @pytest.mark.capability
    def test_get_todos_filter_by_description(self, api):
        """Verify filtering via URL Query Parameters: /todos?description=..."""
        unique_desc = "FoundThisDescription"
        api.post("/todos", json={"title": "Test", "description": unique_desc})
        
        resp = api.get(f"/todos?description={unique_desc}")
        assert resp.status_code == 200
        # Ensure only the matching description is returned
        for todo in resp.json()["todos"]:
            assert todo["description"] == unique_desc

    # 6. Format: JSON Response
    @pytest.mark.capability
    def test_get_todos_json_format(self, api):
        """Verify JSON response structure and headers."""
        resp = api.get("/todos", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert "application/json" in resp.headers["Content-Type"]

    # 7. Format: XML Response
    @pytest.mark.capability
    def test_get_todos_xml_format(self, api):
        """Verify XML response structure and headers."""
        resp = api.get("/todos", headers={"Accept": "application/xml"})
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["Content-Type"]
        # Basic check for XML tags
        assert "<todos>" in resp.text

    # 8. Side Effects: GET is idempotent
    @pytest.mark.capability
    def test_get_todos_no_side_effects(self, api):
        """Verify that GET /todos does not modify any data in the system."""
        state_before = api.get("/todos").json()
        
        # Repeated calls
        api.get("/todos")
        api.get("/todos")
        
        state_after = api.get("/todos").json()
        assert state_before == state_after

    # 9. Error Case: Filter by non-existent criteria
    @pytest.mark.error
    def test_get_todos_filter_no_results(self, api):
        """Verify filtering for a non-existent item returns an empty list."""
        resp = api.get("/todos?title=ThisTitleShouldNotExist12345")
        assert resp.status_code == 200
        assert len(resp.json()["todos"]) == 0

    # 10. Error Case: Malformed Headers
    @pytest.mark.error
    def test_get_todos_malformed_accept_header(self, api):
        """Verify behavior when Accept header is nonsense."""
        resp = api.get("/todos", headers={"Accept": "not-a-real-format"})
        # Usually results in 406 Not Acceptable or defaults to JSON
        assert resp.status_code in [406]
