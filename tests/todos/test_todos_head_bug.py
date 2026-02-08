import pytest

class TestTodosHeadBug:

    # 1. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /todos uses chunked encoding, missing Content-Length header")
    def test_head_todos_documented_metadata_expected(self, api):
        """
        -Bug: HEAD /todos should return the size of the resource via Content-Length.
        Documentation implies a standard response, but server uses Transfer-Encoding: chunked.
        """
        resp = api.head("/todos")
        
        # This will fail because the API is currently buggy/non-standard
        assert resp.status_code == 200
        assert "Content-Length" in resp.headers, "API should provide Content-Length for HEAD requests"
        assert int(resp.headers["Content-Length"]) > 0

    # 2. Bug Case: Observed Behavior (Passing)
    @pytest.mark.bug
    def test_head_todos_actual_chunked_behavior(self, api):
        """
        -Bug: Documents that the server uses chunked encoding for HEAD, 
        which hides the resource size.
        THIS WILL PASS.
        """
        resp = api.head("/todos")
        
        assert resp.status_code == 200
        # This confirms why Content-Length was missing
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert resp.headers.get("Content-Length") is None
        
   # 3. Capability: Method Existence
    @pytest.mark.capability
    def test_head_todos_status_code(self, api):
        """Verify the endpoint at least acknowledges the HEAD method."""
        resp = api.head("/todos")
        assert resp.status_code == 200

    # 4. Side Effect: Safety
    @pytest.mark.capability
    def test_head_todos_no_side_effects(self, api):
        """Verify HEAD does not modify the collection count."""
        count_before = len(api.get("/todos").json()["todos"])
        api.head("/todos")
        count_after = len(api.get("/todos").json()["todos"])
        assert count_before == count_after

    # 5. Error Case: HEAD on non-existent ID
    @pytest.mark.error
    def test_head_todo_invalid_id(self, api):
        """Verify HEAD on a non-existent ID returns 404."""
        # Using your suggested 'extreme' IDs
        for invalid_id in [0, -1, 9999]:
            resp = api.head(f"/todos/{invalid_id}")
            assert resp.status_code == 404