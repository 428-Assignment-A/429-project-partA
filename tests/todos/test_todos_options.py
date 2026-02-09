import pytest

class TestTodosCollectionOptions:
    """
    Consolidated module for OPTIONS /todos.
    Focuses on the gap between current server logic and REST discovery standards.
    """

    # --- ACTUAL BEHAVIOR (Documenting the Current Build) ---

    # 1. Observed Behavior: Empty Body Persistence
    @pytest.mark.capability
    def test_options_todos_actual_empty_body_standard(self, api):
        """Actual: Verifies that OPTIONS returns 200 OK with an empty body (RFC compliant)."""
        resp = api.options("/todos")
        assert resp.status_code == 200
        # While discovery bodies are nice, an empty body is technically valid HTTP.
        assert len(resp.text.strip()) == 0

    # 2. Observed Bug: Greedy Routing (immediate sub-path)
    @pytest.mark.bug
    def test_options_todos_actual_greedy_routing_bug(self, api):
        """
        Actual: Immediate sub-paths incorrectly return 200 OK.
        This confirms the 'Greedy Routing' flaw in the server's path matching.
        """
        resp = api.options("/todos/non-existent-subpath")
        # In a bug-free router, this should be 404. 
        # If it returns 200, it's a documentation/routing defect.
        assert resp.status_code == 200 

    # 3. Capability: Safety & Idempotency
    @pytest.mark.capability
    def test_options_todos_actual_is_safe_and_idempotent(self, api):
        """Actual: Confirms OPTIONS does not modify the collection state."""
        initial_state = api.get("/todos").json().get("todos", [])
        
        api.options("/todos")
        
        final_state = api.get("/todos").json().get("todos", [])
        assert initial_state == final_state

    # --- EXPECTED BEHAVIOR (Standard Requirements / XFAIL) ---

    # 4. Bug: Missing Discovery Payload (XFAIL)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: API provides no discovery body for automated client mapping")
    def test_options_todos_expected_discovery_content(self, api):
        """Expected: OPTIONS should return a body detailing methods (JSON/XML)."""
        for accept in ["application/json", "application/xml"]:
            resp = api.options("/todos", headers={"Accept": accept})
            assert resp.status_code == 200
            assert len(resp.text.strip()) > 0

    # 5. Requirement: Comprehensive Allow Header
    @pytest.mark.capability
    def test_options_todos_expected_allow_header_integrity(self, api):
        """Requirement: Allow header must accurately reflect collection-level verbs."""
        resp = api.options("/todos")
        assert "Allow" in resp.headers
        
        allowed_methods = [m.strip() for m in resp.headers["Allow"].split(",")]
        # Collection level should support these
        for method in ["GET", "POST", "OPTIONS", "HEAD"]:
            assert method in allowed_methods