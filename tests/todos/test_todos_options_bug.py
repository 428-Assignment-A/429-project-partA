import pytest

class TestTodosOptionsBug:

    # 1. Bug Case: Expected Behavior (Failing)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: OPTIONS /todos body is empty, missing discovery payload")
    def test_options_todos_documented_behavior_expected(self, api):
        """
        -Bug: Documentation implies discovery body; observed is empty.
        Expected: Status 200 and 'Allow' header + descriptive body.
        """
        resp = api.options("/todos")
        assert resp.status_code == 200
        # Fail if discovery info is missing
        assert "Allow" in resp.headers
        assert len(resp.text.strip()) > 0

    # 2. Bug Case: Observed Behavior (Passing)
    @pytest.mark.bug
    def test_options_todos_actual_empty_discovery(self, api):
        """
        -Bug: Observed behavior is 200 OK but the body is empty.
        Documents the 'Empty Discovery' defect at the collection level.
        """
        resp = api.options("/todos")
        assert resp.status_code == 200
        assert len(resp.text.strip()) == 0

    #3. Bug Case: Broken 404 for Collection Sub-paths (EXPECTED 404)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: API incorrectly returns 200 for OPTIONS on invalid sub-paths")
    def test_options_todos_invalid_subpath_expected_behavior(self, api):
        """
        Standard REST: OPTIONS on a path that doesn't exist should be 404.
        """
        resp = api.options("/todos/non-existent-path")
        assert resp.status_code == 404 # This will fail because API returns 200

    # 4. Capability: Method Discovery
    @pytest.mark.capability
    def test_options_todos_methods(self, api):
        """Verify the collection level lists standard methods."""
        resp = api.options("/todos")
        allow = resp.headers.get("Allow", "")
        assert "GET" in allow
        assert "POST" in allow

    # 5. Side Effect: OPTIONS Safety
    @pytest.mark.capability
    def test_options_todos_no_side_effect(self, api):
        """Verify OPTIONS does not modify the todo collection."""
        initial_count = len(api.get("/todos").json()["todos"])
        api.options("/todos")
        final_count = len(api.get("/todos").json()["todos"])
        assert initial_count == final_count