import pytest

class TestTodosCollectionOptionsActual:
    """
    ACTUAL BEHAVIOR: Documents the current build of the API.
    All tests here should PASS on the current server.
    """

    # 1. Observed Behavior: Empty Body
    @pytest.mark.capability
    def test_options_todos_actual_is_empty(self, api):
        """Actual: Verifies that OPTIONS /todos returns a 200 OK with no body."""
        resp = api.options("/todos")
        assert resp.status_code == 200
        assert len(resp.text.strip()) == 0

    # 2. Observed Bug: Greedy Routing 
    @pytest.mark.bug
    def test_options_todos_actual_greedy_routing(self, api):
        """Actual: Confirms the router incorrectly accepts sub-paths for OPTIONS."""
        # This asserts the CURRENT reality (200 OK) even though it's technically a bug.
        resp = api.options("/todos/invalid_path")
        assert resp.status_code == 200 

    # 3. Capability: Safety (No Side Effects)
    @pytest.mark.capability
    def test_options_todos_is_safe_method(self, api):
        """Actual: Verifies OPTIONS does not modify the collection."""
        before = api.get("/todos").json().get("todos", [])
        api.options("/todos")
        after = api.get("/todos").json().get("todos", [])
        assert before == after

    # 4. Performance: Metadata Latency
    @pytest.mark.capability
    def test_options_todos_performance(self, api):
        """Actual: Verifies the OPTIONS response is faster than 100ms."""
        resp = api.options("/todos")
        assert resp.elapsed.total_seconds() < 0.1