import pytest

class TestTodosHeadExpected:

    # 1. Bug: Missing Content-Length for Metadata
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /todos uses chunked encoding, missing Content-Length header")
    def test_head_todos_documented_metadata_expected(self, api):
        """Expected: HEAD /todos should return the size of the resource via Content-Length."""
        resp = api.head("/todos")
        
        assert resp.status_code == 200
        # Failure point: HEAD responses should not be chunked; they should report size.
        assert "Content-Length" in resp.headers
        assert int(resp.headers["Content-Length"]) >= 0

    # 2. Capability: Resource Existence (Error Case)
    @pytest.mark.error
    def test_head_todos_not_found_standard_expected(self, api):
        """Expected: HEAD returns 404 for invalid resource IDs."""
        for invalid_id in [0, -1, 99999]:
            resp = api.head(f"/todos/{invalid_id}")
            assert resp.status_code == 404

            # 3. Robustness: Metadata Scalability
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: HEAD /todos returns chunked regardless of collection size")
    def test_head_todos_length_increases_with_data_expected(self, api):
        """Expected: Content-Length should increase as more items are added."""
        # Get initial size
        size_empty = int(api.head("/todos").headers.get("Content-Length", 0))
        
        # Add a substantial item
        api.post("/todos", json={"title": "A" * 100, "description": "B" * 500})
        
        size_with_data = int(api.head("/todos").headers.get("Content-Length", 0))
        assert size_with_data > size_empty

    # 4. Standard Compliance: Body Absence
    @pytest.mark.capability
    def test_head_todos_no_body_content_expected(self, api):
        """Expected: HEAD /todos must never return a body, only headers."""
        resp = api.head("/todos")
        assert len(resp.content) == 0