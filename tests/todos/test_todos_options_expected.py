import pytest

class TestTodosCollectionOptionsExpected:
    """
    EXPECTED BEHAVIOR: Documents the REST standards the API should follow.
    Tests that fail due to known bugs are marked with xfail.
    """

    # 1. Expected Requirement: Discovery Payload
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /todos missing discovery body (JSON/XML)")
    def test_options_todos_should_return_discovery_body(self, api):
        """Expected: OPTIONS should return a body describing available methods."""
        resp = api.options("/todos")
        # This will fail (and be marked XFAIL) because the actual body is empty.
        assert len(resp.text.strip()) > 0

    # 2. Expected Requirement: Correct Routing
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /todos should return 404 for invalid sub-paths")
    def test_options_todos_should_404_on_invalid_path(self, api):
        """Expected: Invalid paths should return 404 Not Found."""
        resp = api.options("/todos/invalid_path")
        # This will fail (XFAIL) because the actual server returns 200.
        assert resp.status_code == 404

    # 3. Capability: Header Compliance
    @pytest.mark.capability
    def test_options_todos_must_have_allow_header(self, api):
        """Requirement: Must provide the Allow header with GET, POST, OPTIONS, HEAD."""
        resp = api.options("/todos")
        assert "Allow" in resp.headers
        methods = [m.strip() for m in resp.headers["Allow"].split(",")]
        for m in ["GET", "POST", "OPTIONS", "HEAD"]:
            assert m in methods

    # 4. Robustness: Format Integrity
    @pytest.mark.capability
    def test_options_todos_accept_header_robustness(self, api):
        """Requirement: Server should handle multiple Accept types for OPTIONS without error."""
        for media_type in ["application/json", "application/xml"]:
            resp = api.options("/todos", headers={"Accept": media_type})
            assert resp.status_code == 200