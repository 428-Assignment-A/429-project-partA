import pytest

class TestTodosIdOptionsBug:

    # 1. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /todos/:id returns 200 OK but the body is empty, hindering discovery.")
    def test_options_id_documented_behavior_expected(self, api):
        """
        Expected: A non-empty body containing endpoint documentation.
        Actual: Body is empty string.
        """
        todo_id = api.post("/todos", json={"title": "Doc Expectation"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # This is the line that will trigger the failure
        assert len(resp.text.strip()) > 0

    # 2. Bug Case: Observed Behavior (Passing)
    @pytest.mark.bug
    def test_options_id_actual_behavior_header_only(self, api):
        """
        -Bug: Documents the current implementation where discovery is header-only.
        Observed: 200 OK and valid 'Allow' header, but body is 0 bytes.
        THIS WILL PASS.
        """
        todo_id = api.post("/todos", json={"title": "Reality Check"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # Confirms the 'Allow' header exists but the body is empty
        assert "Allow" in resp.headers
        assert len(resp.text.strip()) == 0

    # 3. Capability: Instance-Level Method Discovery
    @pytest.mark.capability
    def test_options_id_header_contains_instance_methods(self, api):
        """
        Verify the 'Allow' header correctly lists instance-specific methods.
        Expected: GET, PUT, POST, DELETE, HEAD, OPTIONS.
        """
        todo_id = api.post("/todos", json={"title": "Method Check"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        allow = resp.headers.get("Allow", "")
        # These methods are specific to individual resource instances
        for method in ["GET", "PUT", "POST", "DELETE", "OPTIONS"]:
            assert method in allow

    # 4. Capability: Routing Integrity
    @pytest.mark.capability
    def test_options_id_invalid_subpath_returns_404(self, api):
        """Verify that OPTIONS on a non-existent sub-path of an ID correctly 404s."""
        todo_id = api.post("/todos", json={"title": "Path Test"}).json()['id']
        resp = api.options(f"/todos/{todo_id}/fake_path")
        
        assert resp.status_code == 404

    # 5. Side Effect: State Preservation
    @pytest.mark.capability
    def test_options_id_is_safe_method(self, api):
        """Verify OPTIONS follows the HTTP standard as a 'safe' method (no data changes)."""
        todo_id = api.post("/todos", json={"title": "Safe Data"}).json()['id']
        
        api.options(f"/todos/{todo_id}")
        
        # Confirm the resource title was not altered
        check = api.get(f"/todos/{todo_id}")
        assert check.json()['todos'][0]['title'] == "Safe Data"

    # 6. Capability: Response Performance
    @pytest.mark.capability
    def test_options_id_performance(self, api):
        """Verify the OPTIONS discovery responds in less than 100ms."""
        todo_id = api.post("/todos", json={"title": "Speed Test"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        assert resp.elapsed.total_seconds() < 0.1

    # 7. Capability: Global Endpoint Discovery (Impossible Numeric ID)
    @pytest.mark.capability
    def test_options_on_impossible_numeric_id(self, api):
        """
        OPTIONS should return 200 even for an ID that cannot exist (e.g., -1).
        This proves discovery is handled by the router, not the database.
        """
        resp = api.options("/todos/-1")
        assert resp.status_code == 200
        assert "Allow" in resp.headers
        assert "GET" in resp.headers["Allow"]

    # 8. Capability: Global Endpoint Discovery (String ID)
    @pytest.mark.capability
    def test_options_on_string_id(self, api):
        """
        OPTIONS should return 200 even for a non-numeric ID.
        Clients use this to check allowed methods before attempting a request.
        """
        resp = api.options("/todos/invalid-id-format")
        assert resp.status_code == 200
        assert "Allow" in resp.headers