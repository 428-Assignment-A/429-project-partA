import pytest

class TestTodosPost:

    # 1. Capability: Basic Creation
    @pytest.mark.capability
    def test_post_todo_capability(self, api):
        """Confirm we can create a todo with basic fields."""
        payload = {"title": "Normal Todo", "description": "Regular test", "doneStatus": False}
        resp = api.post("/todos", json=payload)
        assert resp.status_code == 201 or resp.status_code == 200
        assert resp.json()["title"] == "Normal Todo"

    # 2. Capability: Long Title (From your table: 500+ A's)
    @pytest.mark.capability
    def test_post_todo_long_title_capability(self, api):
        """Test the API with a massive title string (500+ chars)."""
        long_title = "A" * 500
        resp = api.post("/todos", json={"title": long_title})
        assert resp.status_code == 201 or resp.status_code == 200
        assert resp.json()["title"] == long_title

    # 3. Capability: XSS and Special Characters (From your table)
    @pytest.mark.capability
    def test_post_todo_xss_and_special_chars(self, api):
        """Test XSS script tags and international characters: é, ñ, 中文."""
        xss_title = "<script>alert('xss')</script> & special chars: é, ñ, 中文"
        resp = api.post("/todos", json={"title": xss_title})
        assert resp.status_code == 201 or resp.status_code == 200
        assert resp.json()["title"] == xss_title

    # 4. Format: XML Creation
    @pytest.mark.capability
    def test_post_todo_xml_capability(self, api):
        """Verify todo creation using XML payload."""
        xml_data = "<todo><title>XML Todo</title><description>Created with XML</description></todo>"
        headers = {"Content-Type": "application/xml", "Accept": "application/xml"}
        resp = api.post("/todos", data=xml_data, headers=headers)
        assert resp.status_code == 201 or resp.status_code == 200
        assert "XML Todo" in resp.text

    # 5. Error Case: Malformed JSON
    @pytest.mark.error
    def test_post_malformed_json_error(self, api):
        """Verify 400 error for broken JSON syntax."""
        broken_json = '{"title": "broken", "description": "missing brace"'
        headers = {"Content-Type": "application/json"}
        resp = api.post("/todos", data=broken_json, headers=headers)
        assert resp.status_code == 400

    # 6. Error Case: Malformed XML
    @pytest.mark.error
    def test_post_malformed_xml_error(self, api):
        """Verify 400 error for broken XML syntax."""
        broken_xml = "<todo><title>Broken</title/todo>"
        headers = {"Content-Type": "application/xml"}
        resp = api.post("/todos", data=broken_xml, headers=headers)
        assert resp.status_code == 400

    # 7. Side Effect: ID Increment
    @pytest.mark.capability
    def test_post_id_increment_logic(self, api):
        """Verify generated ID is roughly [last_id] + 1."""
        resp1 = api.post("/todos", json={"title": "First"})
        id1 = int(resp1.json()["id"])
        resp2 = api.post("/todos", json={"title": "Second"})
        id2 = int(resp2.json()["id"])
        assert id2 > id1

    # 8. Return Code: Success Code Check
    @pytest.mark.capability
    def test_post_returns_success_code(self, api):
        """Confirm return code is in the 200-201 range."""
        resp = api.post("/todos", json={"title": "Code Check"})
        assert resp.status_code in [200, 201]

    # 9. Bug Case: Expected Behavior (FAILING)
    @pytest.mark.bug
    @pytest.mark.xfail(reason="API fails to return 400 for invalid data types")
    def test_post_todo_type_validation_expected(self, api):
        """Expected: API should reject non-string titles with 400 Bad Request."""
        payload = {"title": True}
        resp = api.post("/todos", json=payload)
        assert resp.status_code == 400

    # 10 Bug Case: Actual Behavior (PASSING)
    @pytest.mark.bug
    def test_post_todo_type_validation_actual(self, api):
        """Actual: API accepts invalid types and returns 201 Created."""
        payload = {"title": True}
        resp = api.post("/todos", json=payload)
        # We assert 201 here because this is the CURRENT (buggy) behavior
        assert resp.status_code == 201 
        # Check that it converted 'True' to a string or accepted it
        assert str(resp.json()["title"]) == "true"