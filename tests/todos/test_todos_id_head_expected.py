import pytest

class TestTodosIdHeadExpected:

    # 1. Bug: Content-Length Missing
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /todos/:id returns Transfer-Encoding: chunked instead of Content-Length")
    def test_head_id_documented_metadata_expected(self, api):
        """Expected: HEAD /todos/:id should return the Content-Length of the resource."""
        todo_id = api.post("/todos", json={"title": "Size Check"}).json()['id']
        
        resp = api.head(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # Failure point: Standard requires Content-Length for non-chunked HEAD responses
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) > 0

    # 2. Capability: Resource Existence
    @pytest.mark.error
    def test_head_id_not_found_standard_expected(self, api):
        """Expected: HEAD returns 404 for a non-existent resource ID."""
        resp = api.head("/todos/999999")
        assert resp.status_code == 404

    # 3. Capability: Method Consistency
    @pytest.mark.capability
    def test_head_id_vs_get_consistency_expected(self, api):
        """Expected: HEAD status code must match GET status code for the same resource."""
        todo_id = api.post("/todos", json={"title": "Match Test"}).json()['id']
        
        head_status = api.head(f"/todos/{todo_id}").status_code
        get_status = api.get(f"/todos/{todo_id}").status_code
        
        assert head_status == get_status

# 4. Standard Compliance: Empty Body
    @pytest.mark.capability
    def test_head_id_must_not_have_body_expected(self, api):
        """Expected: HEAD response must never contain a message body."""
        todo_id = api.post("/todos", json={"title": "No Body Test"}).json()['id']
        resp = api.head(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        assert len(resp.content) == 0 