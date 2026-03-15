import pytest

class TestTodosIdHead:
    """
    Test module for HEAD /todos/:id.
    
    Purpose:
    - Main Flow: Verify HEAD for a specific ID returns headers identical to GET.
    - Alternative Flow: Verify metadata consistency across different task IDs.
    - Error Flow: Handle non-existent IDs.
    """

    # 1. Main Flow: Success & Header Parity
    @pytest.mark.capability
    def test_head_id_matches_get_metadata(self, api):
        """
        Main Flow: Verify HEAD /todos/:id returns same metadata as GET /todos/:id.
        Verifies the 'twin' relationship between HEAD and GET headers.
        """
        # Setup: Create a resource to query
        todo_id = api.post("/todos", json={"title": "Main Flow Test"}).json()['id']
        
        head_resp = api.head(f"/todos/{todo_id}")
        get_resp = api.get(f"/todos/{todo_id}")

        assert head_resp.status_code == 200
        assert len(head_resp.content) == 0

        # Compare essential metadata
        # We check Content-Type and Transfer-Encoding (chunked) to ensure consistency
        for header in ["Content-Type", "Transfer-Encoding", "Server"]:
            assert head_resp.headers.get(header) == get_resp.headers.get(header)

    # 2. Alternative Flow: Resource Differentiation
    @pytest.mark.capability
    def test_head_id_consistency_across_different_resources(self, api):
        """
        Alternative Flow: Verify HEAD behavior is consistent for resources 
        with different content lengths/titles.
        """
        id_a = api.post("/todos", json={"title": "Short"}).json()['id']
        id_b = api.post("/todos", json={"title": "A significantly longer title for testing"}).json()['id']

        resp_a = api.head(f"/todos/{id_a}")
        resp_b = api.head(f"/todos/{id_b}")

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200
        # Both should still report as chunked regardless of content size
        assert resp_a.headers.get("Transfer-Encoding") == "chunked"
        assert resp_b.headers.get("Transfer-Encoding") == "chunked"

    # 3. Error Flow: Resource Non-Existence
    @pytest.mark.error
    def test_head_id_not_found(self, api):
        """
        Error Flow: Verify HEAD returns 404 for non-existent resource IDs.
        """
        invalid_ids = [999999, 0, -5]
        for item_id in invalid_ids:
            resp = api.head(f"/todos/{item_id}")
            assert resp.status_code == 404
            assert len(resp.content) == 0

    # 4. Capability: Safety (No Side Effects)
    @pytest.mark.capability
    def test_head_id_is_safe_method(self, api):
        """
        Verifies that a HEAD request to a specific ID does not modify its data.
        """
        todo_id = api.post("/todos", json={"title": "Original Title"}).json()['id']
        
        # Action: HEAD request
        api.head(f"/todos/{todo_id}")
        
        # Verification: Data remains identical
        current_data = api.get(f"/todos/{todo_id}").json()
        assert current_data['todos'][0]['title'] == "Original Title"

    # 5. Performance: Metadata Speed
    @pytest.mark.capability
    def test_head_id_performance(self, api):
        """
        Verifies that HEAD responses for specific IDs are processed rapidly.
        """
        todo_id = api.post("/todos", json={"title": "Performance Test"}).json()['id']
        resp = api.head(f"/todos/{todo_id}")
        
        # Metadata-only requests should be under 100ms
        assert resp.elapsed.total_seconds() < 0.1