import pytest

class TestTodosHeadCollection:
    """
    Test module for the HEAD /todos endpoint.
    Focus: Collection-level metadata, header parity, and error handling.
    """

    # 1. Main Flow: Success & Header Parity
    @pytest.mark.capability
    def test_head_todos_matches_get_metadata(self, api):
        """
        Main Flow: Verify HEAD /todos headers match GET /todos headers.
        Since the server is chunked, we compare metadata instead of byte length.
        """
        head_resp = api.head("/todos")
        get_resp = api.get("/todos")

        # Basic Requirement
        assert head_resp.status_code == 200
        assert len(head_resp.content) == 0

        # Alternative Flow: Header Consistency
        # Verifies that HEAD provides the exact same metadata as a full GET
        headers_to_check = ["Content-Type", "Transfer-Encoding", "Server"]
        for header in headers_to_check:
            assert head_resp.headers.get(header) == get_resp.headers.get(header)

    # 2. Alternative Flow: State Independence
    @pytest.mark.capability
    def test_head_todos_consistent_across_states(self, api):
        """
        Alternative Flow: Verify HEAD behaves consistently regardless of collection size.
        Ensures the metadata remains valid even after data changes.
        """
        # Capture headers when potentially empty/current state
        headers_initial = api.head("/todos").headers

        # Change state (Add an item)
        api.post("/todos", json={"title": "State Change Test"})

        # Capture headers again
        headers_after = api.head("/todos").headers

        # Metadata should remain consistent in structure/type
        assert headers_initial.get("Content-Type") == headers_after.get("Content-Type")
        assert headers_initial.get("Transfer-Encoding") == "chunked"

    # 3. Error Case: Invalid Method/Path Combinations
    @pytest.mark.error
    def test_head_todos_not_found_on_malformed_path(self, api):
        """
        Error Flow: Verify HEAD returns 404 for non-existent collection paths.
        """
        invalid_paths = ["/todos_invalid", "/todo", "/todos/undefined"]
        for path in invalid_paths:
            resp = api.head(path)
            assert resp.status_code == 404
            assert len(resp.content) == 0

    # 4. Capability: Side-Effect Verification (Safety)
    @pytest.mark.capability
    def test_head_todos_is_safe_operation(self, api):
        """
        Verifies that HEAD /todos is a 'safe' method (no side effects).
        """
        # Get baseline via GET
        before_data = api.get("/todos").json().get("todos", [])
        
        # Action
        api.head("/todos")
        
        # Verify no change
        after_data = api.get("/todos").json().get("todos", [])
        assert len(before_data) == len(after_data)

    # 5. Performance: Efficiency
    @pytest.mark.capability
    def test_head_todos_timing_efficiency(self, api):
        """
        Verifies that HEAD returns quickly as it has no body payload.
        """
        resp = api.head("/todos")
        # HEAD should be near-instantaneous for metadata only
        assert resp.elapsed.total_seconds() < 0.2