import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the interoperability features directory
scenarios('../features/interoperability')


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def context():
    """State object to share dynamic IDs and responses between steps."""
    class State:
        def __init__(self):
            self.response = None
            self.captured_id = None
            self.captured_todo_id = None
            self.captured_project_id = None
            self.captured_category_id = None
    return State()


# ==========================================
# GIVEN STEPS (Backgrounds / Setup)
# ==========================================

@given("the todo manager service is running")
def service_running():
    pass


@given("the system is cleared")
def clear_system(api):
    """Delete all todos, projects, and categories to restore a clean state."""
    todos = api.get("/todos").json().get("todos", [])
    for t in todos:
        api.delete(f"/todos/{t['id']}")

    projects = api.get("/projects").json().get("projects", [])
    for p in projects:
        api.delete(f"/projects/{p['id']}")

    categories = api.get("/categories").json().get("categories", [])
    for c in categories:
        api.delete(f"/categories/{c['id']}")


@given(parsers.parse('a project exists with title "{title}" and description "{description}" and active "{active}"'))
def project_exists_full(api, context, title, description, active):
    resp = api.post("/projects", json={
        "title": title,
        "description": description,
        "active": active == "true",
    })
    assert resp.status_code == 201, f"Failed to create project: {resp.text}"
    context.captured_project_id = resp.json()["id"]


@given(parsers.parse('a project exists with title "{title}"'))
def project_exists_title_only(api, context, title):
    resp = api.post("/projects", json={"title": title})
    assert resp.status_code == 201, f"Failed to create project: {resp.text}"
    context.captured_project_id = resp.json()["id"]


@given("I store the id of the created project")
def store_project_id(context):
    assert context.captured_project_id is not None, "No project ID to store"


@given(parsers.parse('a todo is created with title "{title}"'))
def create_todo_with_title(api, context, title):
    resp = api.post("/todos", json={"title": title})
    assert resp.status_code == 201, f"Failed to create todo: {resp.text}"
    context.captured_todo_id = resp.json()["id"]
    context.captured_id = context.captured_todo_id


@given("I capture its dynamic ID")
def capture_dynamic_id(context):
    assert context.captured_todo_id is not None, "No todo ID to capture"


@given(parsers.parse('a category is created with title "{title}" and its ID is captured'))
def create_category_and_capture(api, context, title):
    resp = api.post("/categories", json={"title": title})
    assert resp.status_code == 201, f"Failed to create category: {resp.text}"
    context.captured_category_id = resp.json()["id"]


@given("the todo is linked to the project")
def link_todo_to_project(api, context):
    resp = api.post(
        f"/projects/{context.captured_project_id}/tasks",
        json={"id": context.captured_todo_id}
    )
    assert resp.status_code == 201, f"Failed to link todo to project: {resp.text}"


@given("the category is linked to the todo")
def link_category_to_todo(api, context):
    resp = api.post(
        f"/todos/{context.captured_todo_id}/categories",
        json={"id": context.captured_category_id}
    )
    assert resp.status_code == 201, f"Failed to link category to todo: {resp.text}"


@given("the category is linked to the project")
def link_category_to_project(api, context):
    resp = api.post(
        f"/projects/{context.captured_project_id}/categories",
        json={"id": context.captured_category_id}
    )
    assert resp.status_code == 201, f"Failed to link category to project: {resp.text}"


# ==========================================
# WHEN STEPS (Actions)
# ==========================================

@when(parsers.parse('I POST to "/projects/{stored_project_id}/tasks" with todo ID "{todo_ref}"'))
def post_todo_to_project(api, context, stored_project_id, todo_ref):
    context.response = api.post(
        f"/projects/{context.captured_project_id}/tasks",
        json={"id": context.captured_todo_id}
    )


@when(parsers.parse('I GET "/projects/{stored_project_id}/tasks"'))
def get_project_tasks(api, context, stored_project_id):
    context.response = api.get(f"/projects/{context.captured_project_id}/tasks")


@when(parsers.parse('I GET "/projects/{stored_project_id}/tasks" with Accept header "{format}"'))
def get_project_tasks_with_format(api, context, stored_project_id, format):
    context.response = api.get(
        f"/projects/{context.captured_project_id}/tasks",
        headers={"Accept": format}
    )


@when(parsers.parse('I POST to "/projects/{invalid_id}/tasks" with todo ID stored_todo_id'))
def post_todo_to_invalid_project(api, context, invalid_id):
    context.response = api.post(
        f"/projects/{invalid_id}/tasks",
        json={"id": context.captured_todo_id}
    )


@when(parsers.parse('I DELETE "/projects/{stored_project_id}/tasks/{stored_todo_id}"'))
def delete_todo_from_project(api, context, stored_project_id, stored_todo_id):
    context.response = api.delete(
        f"/projects/{context.captured_project_id}/tasks/{context.captured_todo_id}"
    )


@when(parsers.parse('I DELETE "/projects/{project_id}/tasks/{todo_id}"'))
def delete_todo_from_project_by_ids(api, context, project_id, todo_id):
    context.response = api.delete(f"/projects/{project_id}/tasks/{todo_id}")


@when(parsers.parse('I POST to "/todos/{stored_todo_id}/categories" with category ID "{category_ref}"'))
def post_category_to_todo(api, context, stored_todo_id, category_ref):
    context.response = api.post(
        f"/todos/{context.captured_todo_id}/categories",
        json={"id": context.captured_category_id}
    )


@when(parsers.parse('I GET "/todos/{stored_todo_id}/categories"'))
def get_todo_categories(api, context, stored_todo_id):
    context.response = api.get(f"/todos/{context.captured_todo_id}/categories")


@when(parsers.parse('I GET "/todos/{stored_todo_id}/categories" with Accept header "{format}"'))
def get_todo_categories_with_format(api, context, stored_todo_id, format):
    context.response = api.get(
        f"/todos/{context.captured_todo_id}/categories",
        headers={"Accept": format}
    )


@when(parsers.parse('I POST to "/todos/{stored_todo_id}/categories" with category ID "{invalid_id}"'))
def post_invalid_category_to_todo(api, context, stored_todo_id, invalid_id):
    context.response = api.post(
        f"/todos/{context.captured_todo_id}/categories",
        json={"id": invalid_id}
    )


@when(parsers.parse('I POST to "/projects/{stored_project_id}/categories" with category ID "{category_ref}"'))
def post_category_to_project(api, context, stored_project_id, category_ref):
    context.response = api.post(
        f"/projects/{context.captured_project_id}/categories",
        json={"id": context.captured_category_id}
    )


@when(parsers.parse('I GET "/projects/{stored_project_id}/categories"'))
def get_project_categories(api, context, stored_project_id):
    context.response = api.get(f"/projects/{context.captured_project_id}/categories")


@when(parsers.parse('I POST to "/projects/{invalid_project_id}/categories" with category ID stored_category_id'))
def post_category_to_invalid_project(api, context, invalid_project_id):
    context.response = api.post(
        f"/projects/{invalid_project_id}/categories",
        json={"id": context.captured_category_id}
    )


@when(parsers.parse('I DELETE "/projects/{stored_project_id}"'))
def delete_project(api, context, stored_project_id):
    context.response = api.delete(f"/projects/{context.captured_project_id}")


@when("I DELETE the captured category ID")
def delete_captured_category(api, context):
    context.response = api.delete(f"/categories/{context.captured_category_id}")


@when(parsers.parse('I GET "{url}"'))
def get_url(api, context, url):
    context.response = api.get(url)


# ==========================================
# THEN STEPS (Assertions)
# ==========================================

@then(parsers.parse('the response status should be "{status}"'))
def check_status(context, status):
    assert str(context.response.status_code) == status, \
        f"Expected {status}, got {context.response.status_code}: {context.response.text}"


@then("the response body should contain an error message")
def check_error_body(context):
    data = context.response.json()
    errors = data.get("errorMessages", [])
    assert len(errors) > 0, f"Expected error messages but got: {data}"


@then("a GET request to the captured category ID should return the linked category")
def get_project_categories_contains_category(api, context):
    resp = api.get(f"/projects/{context.captured_project_id}/categories")
    assert resp.status_code == 200
    category_ids = [c["id"] for c in resp.json().get("categories", [])]
    assert context.captured_category_id in category_ids, \
        f"Category {context.captured_category_id} not found in {category_ids}"


@then("a GET request to the captured category ID should return the linked todo")
def get_project_tasks_contains_todo(api, context):
    resp = api.get(f"/projects/{context.captured_project_id}/tasks")
    assert resp.status_code == 200
    todo_ids = [t["id"] for t in resp.json().get("todos", [])]
    assert context.captured_todo_id in todo_ids, \
        f"Todo {context.captured_todo_id} not found in {todo_ids}"


@then(parsers.parse('a GET request to "/projects/{stored_project_id}/tasks" should return the linked todo'))
def verify_project_has_todo(api, context, stored_project_id):
    resp = api.get(f"/projects/{context.captured_project_id}/tasks")
    assert resp.status_code == 200
    todo_ids = [t["id"] for t in resp.json().get("todos", [])]
    assert context.captured_todo_id in todo_ids, \
        f"Todo {context.captured_todo_id} not found in project tasks: {todo_ids}"


@then("a GET request to the captured category ID should return the linked category")
def verify_todo_has_category(api, context):
    resp = api.get(f"/todos/{context.captured_todo_id}/categories")
    assert resp.status_code == 200
    category_ids = [c["id"] for c in resp.json().get("categories", [])]
    assert context.captured_category_id in category_ids, \
        f"Category {context.captured_category_id} not found in todo categories: {category_ids}"


@then(parsers.parse('a GET request to "/todos/{stored_todo_id}/categories" should return the linked category'))
def verify_todo_has_category_explicit(api, context, stored_todo_id):
    resp = api.get(f"/todos/{context.captured_todo_id}/categories")
    assert resp.status_code == 200
    category_ids = [c["id"] for c in resp.json().get("categories", [])]
    assert context.captured_category_id in category_ids, \
        f"Category {context.captured_category_id} not found in: {category_ids}"


@then(parsers.parse('the "{header_name}" header should contain "{format}"'))
def check_header(context, header_name, format):
    actual = context.response.headers.get(header_name, "").lower()
    assert format.lower() in actual, \
        f"Expected '{format}' in header '{header_name}', got '{actual}'"


@then(parsers.parse('the response should contain the linked todo title "{title}"'))
def check_response_contains_todo_title(context, title):
    todos = context.response.json().get("todos", [])
    titles = [t["title"] for t in todos]
    assert title in titles, f"Expected '{title}' in todo titles: {titles}"


@then(parsers.parse('the response should contain the category title "{title}"'))
def check_response_contains_category_title(context, title):
    categories = context.response.json().get("categories", [])
    titles = [c["title"] for c in categories]
    assert title in titles, f"Expected '{title}' in category titles: {titles}"


@then("a GET request to the captured category ID should not contain the todo")
def verify_project_tasks_excludes_todo(api, context):
    resp = api.get(f"/projects/{context.captured_project_id}/tasks")
    assert resp.status_code == 200
    todo_ids = [t["id"] for t in resp.json().get("todos", [])]
    assert context.captured_todo_id not in todo_ids, \
        f"Todo {context.captured_todo_id} should have been unlinked but still found"


@then(parsers.parse('a GET request to "/todos/{stored_todo_id}" should return "{status}"'))
def verify_todo_status(api, context, stored_todo_id, status):
    resp = api.get(f"/todos/{context.captured_todo_id}")
    assert str(resp.status_code) == status, \
        f"Expected {status} for todo {context.captured_todo_id}, got {resp.status_code}"


@then(parsers.parse('a GET request to "/projects/{stored_project_id}" should return "{status}"'))
def verify_project_status(api, context, stored_project_id, status):
    resp = api.get(f"/projects/{context.captured_project_id}")
    assert str(resp.status_code) == status, \
        f"Expected {status} for project {context.captured_project_id}, got {resp.status_code}"
