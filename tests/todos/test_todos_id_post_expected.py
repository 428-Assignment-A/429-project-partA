import pytest

class TestTodosIdPost:

    # 1. Bug Case: Expected Behavior (FAILING)
    # This test is expected to fail due to a known bug where the API accepts a boolean value for the title field instead of rejecting it with a 400 status code.
    @pytest.mark.bug
    @pytest.mark.xfail(reason="Bug: Update endpoint fails to return 400 for invalid data types (Boolean as Title)")
    def test_post_update_type_validation_expected(self, api):
        """Expected: Reject boolean title with 400."""
        todo_id = api.post("/todos", json={"title": "Init"}).json()['id']
        resp = api.post(f"/todos/{todo_id}", json={"title": True})
        assert resp.status_code == 400

    # 2. Capability: send same update twice (idempotency)
    @pytest.mark.capability
    def test_post_update_idempotency(self, api):
        """Expected: Sending the same update twice should not create side effects."""
        todo_id = api.post("/todos", json={"title": "Original"}).json()['id']
        
        # Action 1
        api.post(f"/todos/{todo_id}", json={"title": "Duplicate"})
        state_1 = api.get(f"/todos/{todo_id}").json()
        
        # Action 2 (Repeat)
        api.post(f"/todos/{todo_id}", json={"title": "Duplicate"})
        state_2 = api.get(f"/todos/{todo_id}").json()
        
        assert state_1 == state_2


    # 3. Side Effect: System State Preservation (Checklist Requirement)
    @pytest.mark.capability
    def test_post_update_isolation_expected(self, api):
        """Expected: Updating one resource must not alter others in the system."""
        id_a = api.post("/todos", json={"title": "Keep Me"}).json()['id']
        id_b = api.post("/todos", json={"title": "Change Me"}).json()['id']
        
        # Update B
        api.post(f"/todos/{id_b}", json={"title": "Changed"})
        
        # Verify A is untouched
        res_a = api.get(f"/todos/{id_a}").json()["todos"][0]
        assert res_a["title"] == "Keep Me"

    # 4. Error Case: Malformed XML (Checklist Requirement)
    @pytest.mark.error
    def test_post_update_malformed_xml_expected(self, api):
        """Expected: Return 400 for syntactically incorrect XML payloads."""
        todo_id = api.post("/todos", json={"title": "XML Test"}).json()['id']
        malformed_xml = "<todo><title>Broken XML" # Missing closing tags
        
        resp = api.post(f"/todos/{todo_id}", 
                        data=malformed_xml, 
                        headers={"Content-Type": "application/xml"})
        assert resp.status_code == 400

    # 5. Capability: Response Formatting (Checklist Requirement)
    @pytest.mark.capability
    @pytest.mark.parametrize("fmt", ["application/json", "application/xml"])
    def test_post_update_respects_accept_header_expected(self, api, fmt):
        """Expected: Response format should match the Accept header requested."""
        todo_id = api.post("/todos", json={"title": "Format Test"}).json()['id']
        
        resp = api.post(f"/todos/{todo_id}", 
                        json={"title": "New"}, 
                        headers={"Accept": fmt})
        
        assert resp.status_code == 200
        assert fmt in resp.headers["Content-Type"]

    # 6. Error Case: Delete-Update Race Condition (Checklist Consideration)
    @pytest.mark.error
    def test_post_update_already_deleted_expected(self, api):
        """Expected: Return 404 if attempting to update a resource that was just deleted."""
        todo_id = api.post("/todos", json={"title": "Gone"}).json()['id']
        api.delete(f"/todos/{todo_id}")
        
        resp = api.post(f"/todos/{todo_id}", json={"title": "Resurrect?"})
        assert resp.status_code == 404