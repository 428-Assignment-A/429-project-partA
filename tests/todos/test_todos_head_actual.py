import pytest

class TestTodosHeadActual:

    # 1. Observed Bug: Chunked Encoding
    @pytest.mark.bug
    def test_head_todos_actual_chunked_behavior(self, api):
        """Actual: Documents that the server uses chunked encoding for HEAD responses."""
        resp = api.head("/todos")
        
        assert resp.status_code == 200
        # Confirms the architectural flaw: Chunked is for streaming; HEAD is for metadata.
        assert resp.headers.get("Transfer-Encoding") == "chunked"
        assert "Content-Length" not in resp.headers

    # 2. Capability: Method Support
    @pytest.mark.capability
    def test_head_todos_actual_status_code(self, api):
        """Actual: The endpoint acknowledges the HEAD method with 200 OK."""
        resp = api.head("/todos")
        assert resp.status_code == 200

    # 3. Side Effect: Collection Safety
    @pytest.mark.capability
    def test_head_todos_actual_no_side_effects(self, api):
        """Actual: Verifies HEAD does not modify the collection count."""
        count_before = len(api.get("/todos").json().get("todos", []))
        api.head("/todos")
        count_after = len(api.get("/todos").json().get("todos", []))
        assert count_before == count_after

    # 4. Performance: Header Speed
    @pytest.mark.capability
    def test_head_todos_actual_response_time(self, api):
        """Actual: HEAD requests respond quickly as they transmit no body."""
        resp = api.head("/todos")
        assert resp.elapsed.total_seconds() < 0.1

    # 5. Robustness: Data-Independent Bug Persistence
    @pytest.mark.bug
    def test_head_todos_actual_chunked_regardless_of_population(self, api):
        """Actual: Verifies the chunked bug exists for both empty and populated lists."""
        # Scenario A: Initial state
        resp_initial = api.head("/todos")
        
        # Scenario B: Populated state (add an item)
        api.post("/todos", json={"title": "Data Persistence Check"})
        resp_populated = api.head("/todos")
        
        assert resp_initial.headers.get("Transfer-Encoding") == "chunked"
        assert resp_populated.headers.get("Transfer-Encoding") == "chunked"