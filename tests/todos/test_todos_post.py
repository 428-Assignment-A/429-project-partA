import pytest

class TestTodosPost:

    # 1. Capability: Basic Creation with JSON
    @pytest.mark.capability
    def test_post_todo_json_capability(self, api):
        """Confirm API creates todo using standard JSON fields."""
        payload = {
            "title": "Standard Todo",
            "description": "Verification of basic POST capability",
            "doneStatus": False
        }
        resp = api.post("/todos", json=payload)
        
        assert resp.status_code in [200, 201]
        data = resp.json()
        assert data["title"] == "Standard Todo"
        assert "id" in data
        assert data["doneStatus"] == "false" # API typically returns strings for booleans

    # 2. Capability: Long Title (From Observation Table: 500+ A's)
    @pytest.mark.capability
    def test_post_todo_extreme_length_title_capability(self, api):
        """Confirm API handles extremely long titles (500+ characters)."""
        long_title = "A" * 500
        payload = {"title": long_title}
        resp = api.post("/todos", json=payload)
        
        assert resp.status_code in [200, 201]
        assert resp.json()["title"] == long_title

    # 3. Capability: XSS and Special Characters (From Observation Table)
    @pytest.mark.capability
    def test_post_todo_special_chars_capability(self, api):
        """Confirm API handles XSS scripts and international characters."""
        special_title = "<script>alert('xss')</script> & special chars: é, ñ, 中文"
        payload = {"title": special_title}
        resp = api.post("/todos", json=payload)
        
        assert resp.status_code in [200, 201]
        assert resp.json()["title"] == special_title

    # 4. Format: XML Payload Creation
    @pytest.mark.capability
    def test_post_todo_xml_format(self, api):
        """Verify the API can generate a todo from an XML payload."""
        xml_data = "<todo><title>XML Todo</title><description>Created with XML</description></todo>"
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}
        
        # Passing XML string as 'data' since 'json' parameter handles dicts
        resp = api.post("/todos", data=xml_data, headers=headers)
        
        assert resp.status_code in [200, 201]
        assert "XML Todo" in resp.text
        assert "application/xml" in resp.headers["Content-Type"]

    # 5. Error Case: Malformed JSON Payload
    @pytest.mark.error
    def test_post_todo_malformed_json_error(self, api):
        """Verify API returns 400 for malformed JSON structure."""
        malformed_json = '{"title": "Broken JSON", "description": "missing closing brace"'
        headers = {"Content-Type": "application/json"}
        
        resp = api.post("/todos", data=malformed_json, headers=headers)
        assert resp.status_code == 400

    # 6. Error Case: Malformed XML Payload
    @pytest.mark.error
    def test_post_todo_malformed_xml_error(self, api):
        """Verify API returns 400 for invalid XML structure."""
        malformed_xml = "<todo><title>Broken XML</title/todo>"
        headers = {"Content-Type": "application/xml"}
        
        resp = api.post("/todos", data=malformed_xml, headers=headers)
        assert resp.status_code == 400

    # 7. Side Effects: State Verification
    @pytest.mark.capability
    def test_post_todo_side_effect_count(self, api):
        """Verify that POST only creates one item and doesn't modify others."""
        # Save initial state
        initial_todos = api.get("/todos").json()["todos"]
        initial_count = len(initial_todos)
        
        # Execute
        api.post("/todos", json={"title": "Count Test"})
        
        # Verify state
        final_todos = api.get("/todos").json()["todos"]
        assert len(final_todos) == initial_count + 1
        
        # Confirm old items remain unchanged
        if initial_count > 0:
            assert initial_todos[0] in final_todos

    # 8. Return Code: Correct ID generation
    @pytest.mark.capability
    def test_post_todo_id_increment_logic(self, api):
        """Verify generated IDs are unique and incrementing (Requirement)."""
        resp1 = api.post("/todos", json={"title": "First"})
        id1 = int(resp1.json()["id"])
        
        resp2 = api.post("/todos", json={"title": "Second"})
        id2 = int(resp2.json()["id"])
        
        assert id2 > id1
    
    # 9. Error Case: Empty Title String
    @pytest.mark.error
    def test_post_todo_empty_title_error(self, api):
        """
        Docs say: 'title can not be empty' and 'Mandatory: true'.
        Verify that "" returns 400.
        """
        payload = {"title": ""}
        resp = api.post("/todos", json=payload)
        
        # This SHOULD be 400 based on the documentation
        assert resp.status_code == 400