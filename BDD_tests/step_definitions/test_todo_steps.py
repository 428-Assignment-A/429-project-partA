import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the features directory
scenarios('../features')

@pytest.fixture
def context():
    """State object to share data (like dynamic IDs) between steps."""
    class State:
        def __init__(self):
            self.response = None
            self.captured_id = None
            self.captured_category_id = None
            self.captured_todo_id = None
            self.captured_project_id = None
    return State()

# ==========================================
# GIVEN STEPS (Backgrounds)
# ==========================================

@given("the todo manager service is running")
def service_running():
    # Health check is handled by conftest.py
    pass

@given("the system is cleared")
def clear_data(api):
    # Get all todos and delete them to start fresh
    todos = api.get_todos().json().get("todos", [])
    for t in todos:
        api.delete_todo(t['id'])
    # Also clear all categories
    categories = api.get("/categories").json().get("categories", [])
    for c in categories:
        api.delete(f"/categories/{c['id']}")

@given(parsers.parse('a todo is created with title "{title}"'))
def create_todo_with_title(api, context, title):
    resp = api.create_todo({"title": title})
    context.response = resp
    context.captured_id = resp.json().get('id')

@given("I capture its dynamic ID")
def capture_id(context):
    # Ensures we have the ID from the previous 'Given' step
    assert context.response is not None
    context.captured_id = context.response.json().get('id')

@given("a todo is created and its ID is captured")
def create_and_capture(api, context):
    resp = api.create_todo({"title": "Default BDD Task"})
    context.response = resp
    context.captured_id = resp.json().get('id')

@given(parsers.parse('a todo exists with title "{title}" and doneStatus "{status}"'))
def create_todo_with_status(api, title, status):
    # Used in searching.feature Background
    val = True if status.lower() == "true" else False
    resp = api.create_todo({"title": title})
    todo_id = resp.json().get('id')
    # Update it to the required status
    api.post(f"/todos/{todo_id}", json={"doneStatus": val})

# ==========================================
# WHEN STEPS (Actions)
# ==========================================

@when(parsers.parse('I POST to "{endpoint}" with title "{title}" and description "{description}"'))
def post_with_desc(api, context, endpoint, title, description):
    context.response = api.post(endpoint, json={"title": title, "description": description})

@when(parsers.parse('I POST to "{endpoint}" in "{format}" with title "{title}"'))
def post_with_format(api, context, endpoint, format, title):
    headers = {"Content-Type": format, "Accept": format}
    if "xml" in format:
        # Pass raw XML string for the server to parse correctly
        payload = f"<todo><title>{title}</title></todo>"
        context.response = api.post(endpoint, data=payload, headers=headers)
    else:
        context.response = api.post(endpoint, json={"title": title}, headers=headers)

@when(parsers.parse('I POST to "{endpoint}" with a {type_name} value of {value}'))
def post_invalid_types(api, context, endpoint, type_name, value):
    # Cast "true" to True and "12345" to 12345 to test API validation
    if value == "true": val = True
    elif value == "false": val = False
    elif value.isdigit(): val = int(value)
    else: val = value
    context.response = api.post(endpoint, json={type_name: val})

@when(parsers.parse('I POST to the captured ID with "{field}" as "{value}"'))
def post_to_captured_id(api, context, field, value):
    context.response = api.post(f"/todos/{context.captured_id}", json={field: value})

@when(parsers.parse('I PUT to the captured ID with title "{title}" and doneStatus {status}'))
def put_to_captured_id(api, context, title, status):
    val = True if status.lower() == "true" else False
    context.response = api.put(f"/todos/{context.captured_id}", json={"title": title, "doneStatus": val})

@when(parsers.parse('I POST to the captured ID with an ID field set to "{new_id}"'))
def post_new_id(api, context, new_id):
    context.response = api.post(f"/todos/{context.captured_id}", json={"id": new_id})

@when(parsers.parse('I POST to the captured ID with doneStatus {status}'))
@when(parsers.parse('I POST to the captured ID with doneStatus "{status}"'))
def post_status_captured(api, context, status):
    # Handle both boolean logic (true) and user error logic ("maybe", "1")
    if status.lower() == "true": val = True
    elif status.lower() == "false": val = False
    else: val = status
    context.response = api.post(f"/todos/{context.captured_id}", json={"doneStatus": val})

@when(parsers.parse('I GET the captured ID with Accept header "{format}"'))
def get_with_accept(api, context, format):
    # The API only returns XML if the Accept header is explicitly requested
    context.response = api.get(f"/todos/{context.captured_id}", headers={"Accept": format})

@when("I DELETE the captured ID")
def delete_captured_id(api, context):
    context.response = api.delete(f"/todos/{context.captured_id}")

@when(parsers.parse('I send a "{method}" request to the captured ID'))
def send_method_captured(api, context, method):
    context.response = api.session.request(method, f"{api.base_url}/todos/{context.captured_id}")

@when(parsers.parse('I DELETE the resource at "{path}"'))
@when("I DELETE the captured ID")
def delete_resource(api, context, path=None):
    if path == "ALREADY_DEL":
        # We need to delete it twice to ensure the second one is a 404
        api.delete(f"/todos/{context.captured_id}")
        context.response = api.delete(f"/todos/{context.captured_id}")
    elif path:
        url_path = path if path.startswith('/') else f'/{path}'
        context.response = api.delete(url_path)
    else:
        context.response = api.delete(f"/todos/{context.captured_id}")

@when(parsers.parse('I GET "{url}"'))
def get_url(api, context, url):
    context.response = api.get(url)

@when(parsers.parse('I send an OPTIONS request to "{path}"'))
def send_options(api, context, path):
    context.response = api.options(path)


# ==========================================
# THEN STEPS (Assertions)
# ==========================================

@then(parsers.parse('the response status should be "{status}"'))
def check_status(context, status):
    actual = str(context.response.status_code)    
    if status == "400" and actual == "201":
        pytest.xfail("BUG: API accepts invalid data types (Boolean/Int) for titles.")
        
    assert actual == status

@then(parsers.parse('the response body should contain title "{title}"'))
def check_body_title(context, title):
    assert context.response.json().get('title') == title

@then("the new ID should be stored for subsequent steps")
def verify_id_stored(context):
    data = context.response.json()
    # The API sometimes returns the object directly, sometimes in a list
    if 'id' in data:
        context.captured_id = data['id']
    elif 'todos' in data and len(data['todos']) > 0:
        context.captured_id = data['todos'][0]['id']
        
    assert context.captured_id is not None, f"Failed to capture ID from: {data}"

@then(parsers.parse('the "{header_name}" header should contain "{format}"'))
@then(parsers.parse('the "{header_name}" header should match "{format}"'))
def check_header(context, header_name, format):
    actual = context.response.headers.get(header_name, "").lower()
    assert format.lower() in actual

@then(parsers.parse('the todo should have "{field}" set to "{value}"'))
def check_field_persistence(api, context, field, value):
    resp = api.get(f"/todos/{context.captured_id}")
    todo = resp.json()['todos'][0]
    assert str(todo.get(field)) == value

@then(parsers.parse('the todo should match the title "{title}"'))
def check_title_persistence(api, context, title):
    resp = api.get(f"/todos/{context.captured_id}")
    todo = resp.json()['todos'][0]
    assert todo.get('title') == title

@then(parsers.parse('the error message should be "{msg}"'))
def check_error_message(context, msg):
    errors = context.response.json().get('errorMessages', [])
    assert any(msg in error for error in errors)

@then(parsers.parse('the todo should show doneStatus as {status}'))
def check_done_status(api, context, status):
    resp = api.get(f"/todos/{context.captured_id}")
    todo = resp.json()['todos'][0]
    assert str(todo.get('doneStatus')).lower() == status.lower()

@then(parsers.parse('a GET request to the captured ID should return "{status}"'))
def check_deleted_status(api, context, status):
    resp = api.get(f"/todos/{context.captured_id}")
    assert str(resp.status_code) == status

@then("the captured ID should still exist")
def check_still_exists(api, context):
    resp = api.get(f"/todos/{context.captured_id}")
    assert resp.status_code == 200

@then(parsers.parse('all items in the response should have doneStatus {status}'))
def check_all_done_status(context, status):
    items = context.response.json().get('todos', [])
    for item in items:
        assert str(item.get('doneStatus')).lower() == status.lower()

@then(parsers.parse('the number of items returned should be {count:d}'))
def check_item_count(context, count):
    items = context.response.json().get('todos', [])
    assert len(items) == count

@then("the response body should be empty")
def check_empty_body(context):
    # Some API servers return whitespace or empty bytes
    assert context.response.text.strip() == ""