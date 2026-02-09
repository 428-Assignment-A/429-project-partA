import pytest

class TestTodosIdHeadActual:

    # 1. Observed Bug: Chunked Encoding instead of Length
    @pytest.mark.bug
    def test_head_id_actual_chunked_encoding(self, api):
        """Actual: Documents that the server erroneously uses chunked encoding for HEAD."""
        todo_id = api.post("/todos", json={"title": "Chunked Test"}).json()['id']
        
        resp = api.head(f"/todos/{todo_id}")
        
        assert resp.status_code == 200
        # Confirms the bug: Transfer-Encoding is present, Content-Length is missing
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert "Content-Length" not in resp.headers

    # 2. Observed Behavior: Empty Body
    @pytest.mark.capability
    def test_head_id_actual_no_body(self, api):
        """Actual: Verifies that even with chunked encoding, the response body is empty."""
        todo_id = api.post("/todos", json={"title": "No Body Check"}).json()['id']
        resp = api.head(f"/todos/{todo_id}")
        
        assert len(resp.text) == 0

    # 3. Capability: Safety (No Side Effects)
    @pytest.mark.capability
    def test_head_id_actual_is_safe_method(self, api):
        """Actual: HEAD request does not modify the resource data."""
        todo_id = api.post("/todos", json={"title": "Safe Title"}).json()['id']
        
        api.head(f"/todos/{todo_id}")
        
        # Verify data remains unchanged via GET
        check = api.get(f"/todos/{todo_id}").json()
        assert check['todos'][0]['title'] == "Safe Title"

    # 4. Performance: Response Speed
    @pytest.mark.capability
    def test_head_id_actual_performance(self, api):
        """Actual: HEAD response returns quickly (metadata only)."""
        todo_id = api.post("/todos", json={"title": "Speed"}).json()['id']
        resp = api.head(f"/todos/{todo_id}")
        assert resp.elapsed.total_seconds() < 0.1