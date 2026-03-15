import pytest
import xml.etree.ElementTree as ET
from pytest_bdd import given, when, then, parsers


# ==========================================
# GIVEN STEPS (Backgrounds)
# ==========================================

@given(parsers.parse('a category is created with title "{title}" and its ID is captured'))
def create_category_and_capture(api, context, title):
    resp = api.post("/categories", json={"title": title})
    assert resp.status_code == 201, f"Failed to create category: {resp.text}"
    context.captured_category_id = resp.json().get("id")
    context.captured_id = context.captured_category_id


@given(parsers.parse('a category is created with title "{title}"'))
def create_category_only(api, context, title):
    resp = api.post("/categories", json={"title": title})
    assert resp.status_code == 201, f"Failed to create category: {resp.text}"
    context.captured_category_id = resp.json().get("id")
    context.captured_id = context.captured_category_id


@given("I capture its dynamic category ID")
def capture_dynamic_category_id(context):
    assert context.captured_category_id is not None, "No category ID to capture"


@given(parsers.parse('a category exists with title "{title}" and description "{description}"'))
def create_category_with_description(api, title, description):
    resp = api.post("/categories", json={"title": title, "description": description})
    assert resp.status_code == 201, f"Failed to create category: {resp.text}"


@given(parsers.parse('a todo is created with title "{title}" and its ID is captured'))
def create_todo_and_capture(api, context, title):
    resp = api.post("/todos", json={"title": title})
    assert resp.status_code == 201, f"Failed to create todo: {resp.text}"
    context.captured_todo_id = resp.json().get("id")


@given(parsers.parse('a project is created with title "{title}" and its ID is captured'))
def create_project_and_capture(api, context, title):
    resp = api.post("/projects", json={"title": title})
    assert resp.status_code == 201, f"Failed to create project: {resp.text}"
    context.captured_project_id = resp.json().get("id")


# ==========================================
# WHEN STEPS (Actions)
# ==========================================

@when(parsers.parse('I POST to "{endpoint}" with title "{title}"'))
def post_with_title_only(api, context, endpoint, title):
    context.response = api.post(endpoint, json={"title": title})


@when("I DELETE the captured category ID")
def delete_captured_category(api, context):
    context.response = api.delete(f"/categories/{context.captured_category_id}")


@when(parsers.parse('I send a "{method}" request to the captured category ID'))
def send_method_to_category(api, context, method):
    context.response = api.session.request(
        method, f"{api.base_url}/categories/{context.captured_category_id}"
    )


@when(parsers.parse('I DELETE the category at "{path}"'))
def delete_category_at_path(api, context, path):
    if path == "ALREADY_DELETED":
        api.delete(f"/categories/{context.captured_category_id}")
        context.response = api.delete(f"/categories/{context.captured_category_id}")
    else:
        context.response = api.delete(path)


@when(parsers.parse('I POST to the captured category ID with "{field}" as "{value}"'))
def post_field_to_category(api, context, field, value):
    context.response = api.post(
        f"/categories/{context.captured_category_id}", json={field: value}
    )


@when(parsers.parse('I PUT to the captured category ID with title "{title}" and description "{description}"'))
def put_to_captured_category(api, context, title, description):
    context.response = api.put(
        f"/categories/{context.captured_category_id}",
        json={"title": title, "description": description},
    )


@when(parsers.parse('I POST to the captured category ID with an ID field set to "{new_id}"'))
def post_category_with_new_id(api, context, new_id):
    context.response = api.post(
        f"/categories/{context.captured_category_id}", json={"id": new_id}
    )


@when(parsers.parse('I GET "{url}" with Accept header "{format}"'))
def get_with_accept_format(api, context, url, format):
    context.response = api.get(url, headers={"Accept": format})


@when(parsers.parse('I POST to "/categories/{category_ref}/todos" with the captured todo ID'))
def post_category_todo_link(api, context, category_ref):
    cat_id = context.captured_category_id if category_ref == "CAPTURED_ID" else category_ref
    context.response = api.post(f"/categories/{cat_id}/todos", json={"id": context.captured_todo_id})


@when(parsers.parse('I POST to "/categories/{category_ref}/projects" with the captured project ID'))
def post_category_project_link(api, context, category_ref):
    cat_id = context.captured_category_id if category_ref == "CAPTURED_ID" else category_ref
    context.response = api.post(f"/categories/{cat_id}/projects", json={"id": context.captured_project_id})


@when(parsers.parse('I POST to "/categories/CAPTURED_ID/{endpoint}" with id "{invalid_id}"'))
def post_category_invalid_link(api, context, endpoint, invalid_id):
    context.response = api.post(
        f"/categories/{context.captured_category_id}/{endpoint}",
        json={"id": invalid_id},
    )


# ==========================================
# THEN STEPS (Assertions)
# ==========================================

@then("the new category ID should be stored for subsequent steps")
def store_new_category_id(context):
    data = context.response.json()
    if "id" in data:
        context.captured_category_id = data["id"]
        context.captured_id = context.captured_category_id
    assert context.captured_category_id is not None, f"No category ID found in: {data}"


@then("the response body should contain an error message")
def check_error_body(context):
    data = context.response.json()
    errors = data.get("errorMessages", [])
    assert len(errors) > 0, f"Expected error messages but got: {data}"


@then(parsers.parse('a GET request to the captured category ID should return "{status}"'))
def get_category_by_id_returns_status(api, context, status):
    resp = api.get(f"/categories/{context.captured_category_id}")
    assert str(resp.status_code) == status


@then("the captured category ID should still exist")
def captured_category_still_exists(api, context):
    resp = api.get(f"/categories/{context.captured_category_id}")
    assert resp.status_code == 200


@then(parsers.parse('the category should have "{field}" set to "{value}"'))
def check_category_field_value(api, context, field, value):
    resp = api.get(f"/categories/{context.captured_category_id}")
    categories = resp.json().get("categories", [])
    assert len(categories) > 0, "No categories returned"
    assert str(categories[0].get(field)) == value


@then(parsers.parse('the category should match the title "{title}"'))
def check_category_title_match(api, context, title):
    resp = api.get(f"/categories/{context.captured_category_id}")
    categories = resp.json().get("categories", [])
    assert len(categories) > 0, "No categories returned"
    assert categories[0].get("title") == title


@then(parsers.parse('the number of category items returned should be {count:d}'))
def check_category_item_count(context, count):
    items = context.response.json().get("categories", [])
    assert len(items) == count


@then("the response should contain at least 2 categories")
def check_at_least_two_categories(context):
    content_type = context.response.headers.get("Content-Type", "")
    if "xml" in content_type:
        root = ET.fromstring(context.response.text)
        categories = root.findall(".//category") or list(root)
        assert len(categories) >= 2, f"Expected at least 2 categories, got {len(categories)}"
    else:
        items = context.response.json().get("categories", [])
        assert len(items) >= 2, f"Expected at least 2 categories, got {len(items)}"


@then(parsers.parse('a GET to "/categories/{category_ref}/todos" should include the captured todo ID'))
def get_category_todos_includes_id(api, context, category_ref):
    cat_id = context.captured_category_id if category_ref == "CAPTURED_ID" else category_ref
    resp = api.get(f"/categories/{cat_id}/todos")
    todo_ids = [t.get("id") for t in resp.json().get("todos", [])]
    assert context.captured_todo_id in todo_ids, \
        f"Todo {context.captured_todo_id} not found in {todo_ids}"


@then(parsers.parse('a GET to "/categories/{category_ref}/projects" should include the captured project ID'))
def get_category_projects_includes_id(api, context, category_ref):
    cat_id = context.captured_category_id if category_ref == "CAPTURED_ID" else category_ref
    resp = api.get(f"/categories/{cat_id}/projects")
    project_ids = [p.get("id") for p in resp.json().get("projects", [])]
    assert context.captured_project_id in project_ids, \
        f"Project {context.captured_project_id} not found in {project_ids}"
