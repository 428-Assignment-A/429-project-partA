import pytest

class TestTodosIdOptions:
    """
    Focusing on architectural routing bugs and standard compliance.
    """

    # 1. THE ACTUAL BUG: Greedy Routing
    @pytest.mark.bug
    def test_options_on_invalid_path_returns_200_instead_of_404(self, api):
        """
        BUG: The server incorrectly returns 200 OK for paths that do not exist.
        This violates standard REST routing principles.
        """
        resp = api.options("/todos/this/path/is/fake/and/should/be/404")
        
        # In a healthy API, this should be 404.
        assert resp.status_code == 404 

    # 2. CAPABILITY: Standard Options Behavior
    @pytest.mark.capability
    def test_options_id_standard_behavior(self, api):
        """Confirming the API follows RFC 7231 by providing an Allow header."""
        todo_id = api.post("/todos", json={"title": "Test"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        assert "Allow" in resp.headers
        # Body should be empty per standard, but headers are mandatory
        assert len(resp.text.strip()) == 0

    # 3. SIDE EFFECT: State Preservation
    @pytest.mark.capability
    def test_options_is_safe_method(self, api):
        """Verify that an OPTIONS request does not modify the resource state."""
        todo_id = api.post("/todos", json={"title": "Original"}).json()['id']
        
        # Execute discovery
        api.options(f"/todos/{todo_id}")
        
        # Verify data remains identical
        check = api.get(f"/todos/{todo_id}").json()
        assert check['todos'][0]['title'] == "Original"

    # 4. PERFORMANCE: Discovery Speed
    @pytest.mark.capability
    def test_options_performance_latency(self, api):
        """OPTIONS requests should be extremely fast as they are often pre-flighted."""
        todo_id = api.post("/todos", json={"title": "Speed"}).json()['id']
        resp = api.options(f"/todos/{todo_id}")
        
        # Should respond in less than 100ms
        assert resp.elapsed.total_seconds() < 0.1

    # 5. ROBUSTNESS: Media Type Handling
    @pytest.mark.capability
    def test_options_handles_different_accept_headers(self, api):
        """Ensure the router doesn't crash when specific content types are requested."""
        todo_id = api.post("/todos", json={"title": "Format"}).json()['id']
        
        for content_type in ["application/json", "application/xml"]:
            resp = api.options(f"/todos/{todo_id}", headers={"Accept": content_type})
            assert resp.status_code == 200