import pytest

class TestTodosIdHeadBug:

    # 1. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /todos/:id returns Transfer-Encoding: chunked instead of Content-Length")
    def test_head_id_documented_metadata_expected(self, api):
        """
        -Bug: HEAD /todos/:id should return the Content-Length of the resource.
        Expected: Content-Length header should be present.
        THIS WILL FAIL: The server uses 'Transfer-Encoding: chunked' instead.
        """
        # Setup: Create a todo to ensure there is content to measure
        todo_id = api.post("/todos", json={"title": "Metadata Test"}).json()['id']
        
        resp = api.head(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # This is where it fails:
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 2. Bug Case: Observed Behavior (Passing)
    @pytest.mark.bug
    def test_head_id_actual_chunked_response_bug(self, api):
        """
        -Bug: Documents that HEAD /todos/:id returns 200 OK but hides size via chunking.
        Observed: Transfer-Encoding is 'chunked' and Content-Length is None.
        THIS WILL PASS.
        """
        todo_id = api.post("/todos", json={"title": "Chunked Test"}).json()['id']
        
        resp = api.head(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # Confirms the server is using chunked encoding for a metadata-only request
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert resp.headers.get("Content-Length") is None

    # 3. Error Case: HEAD on Non-Existent ID
    @pytest.mark.error
    def test_head_id_not_found_error(self, api):
        """Verify HEAD correctly returns 404 for an ID that doesn't exist."""
        resp = api.head("/todos/99999")
        assert resp.status_code == 404

    # 4. Capability: Method Consistency
    @pytest.mark.capability
    def test_head_id_vs_get_status_consistency(self, api):
        """Verify that HEAD and GET return identical status codes for the same ID."""
        todo_id = api.post("/todos", json={"title": "Consistency"}).json()['id']
        
        head_resp = api.head(f"/todos/{todo_id}")
        get_resp = api.get(f"/todos/{todo_id}")
        
        assert head_resp.status_code == get_resp.status_code

    # 5. Side Effect: Safety Check
    @pytest.mark.capability
    def test_head_id_is_safe_side_effect(self, api):
        """Verify that HEAD request does not modify the resource data."""
        todo_id = api.post("/todos", json={"title": "Safe"}).json()['id']
        
        api.head(f"/todos/{todo_id}")
        
        # Verify data remains unchanged
        check = api.get(f"/todos/{todo_id}")
        assert check.json()['todos'][0]['title'] == "Safe"