import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the features directory
scenarios('../features/project')

BASE_URL = "http://localhost:4567"
 
 
# ==========================================
# FIXTURES
# ==========================================
 
@pytest.fixture
def context():
    """State object to share dynamic IDs and responses between steps."""
    class State:
        def __init__(self):
            self.response = None
            self.project_id = None
            self.todo_id = None
    return State()
 
 
# ==========================================
# GIVEN STEPS
# ==========================================
 
@given("the todo manager service is running")
def service_running(api):
    try:
        resp = api.get("/projects")
        assert resp.status_code == 200, "Service is not running"
    except requests.exceptions.ConnectionError:
        pytest.fail("Service is not running — could not connect to localhost:4567")
 
 
@given("the system is cleared")
def clear_system(api):
    """Delete all projects and todos to restore initial state."""
    projects = api.get("/projects").json().get("projects", [])
    for p in projects:
        api.delete(f"/projects/{p['id']}")
 
    todos = api.get("/todos").json().get("todos", [])
    for t in todos:
        api.delete(f"/todos/{t['id']}")
 
 
@given(parsers.parse('a project exists with title "{title}" and description "{description}" and active "{active}"'))
def project_exists_full(api, context, title, description, active):
    resp = api.post("/projects", json={
    "title": title,
    "description": description,         
    "active": active == "true",
    })
    assert resp.status_code == 201
    context.project_id = resp.json()["id"]
 
 
@given(parsers.parse('a project exists with title "{title}"'))
def project_exists_title_only(api, context, title):
    resp = api.post("/projects", json={"title": title})
    assert resp.status_code == 201
    context.project_id = resp.json()["id"]
 
 
@given(parsers.parse('a todo exists with title "{title}"'))
def todo_exists(api, context, title):
    resp = api.post("/todos", json={"title": title})
    assert resp.status_code == 201
    context.todo_id = resp.json()["id"]
 
 
@given("the todo is linked to the project")
def link_todo_to_project(api, context):
    resp = api.post(
        f"/projects/{context.project_id}/tasks",
        json={"id": context.todo_id}
    )
    assert resp.status_code == 201
 
 
@given("I store the id of the created project")
def store_project_id(context):
    assert context.project_id is not None, "No project ID to store"
 
 
@given("I store the id of the created todo")
def store_todo_id(context):
    assert context.todo_id is not None, "No todo ID to store"
 
 
# ==========================================
# WHEN STEPS
# ==========================================
 
@when(parsers.parse('I POST to "{endpoint}" with title "{title}" and description "{description}" and active "{active}"'))
def post_project_full(api, context, endpoint, title, description, active):
    context.response = api.post(endpoint, json={
        "title": title,
        "description": description,
        "active": active == "true",
    })
 
 
@when(parsers.parse('I POST to "{endpoint}" with title "{title}"'))
def post_project_title_only(api, context, endpoint, title):
    context.response = api.post(endpoint, json={"title": title})
 
 
@when(parsers.parse('I POST to "{endpoint}" with title "{title}" and field "id" set to "{id}"'))
def post_project_with_id(api, context, endpoint, title, id):
    context.response = api.post(endpoint, json={"title": title, "id": id})
 
 
@when(parsers.parse('I GET "{url}"'))
def get_url(api, context, url):
    context.response = api.get(url)
 
 
@when('I GET "/projects/{stored_id}"')
def get_project_by_stored_id(api, context):
    context.response = api.get(f"/projects/{context.project_id}")
 
 
@when('I GET "/projects/{stored_project_id}"')
def get_project_by_stored_project_id(api, context):
    context.response = api.get(f"/projects/{context.project_id}")
 
 
@when(parsers.parse('I GET "/projects/<id>"'))
def get_project_by_id(api, context, id):
    context.response = api.get(f"/projects/{id}")
 
 
@when('I DELETE "/projects/{stored_id}"')
def delete_project_by_stored_id(api, context):
    context.response = api.delete(f"/projects/{context.project_id}")
 
 
@when('I DELETE "/projects/{stored_project_id}"')
def delete_project_by_stored_project_id(api, context):
    context.response = api.delete(f"/projects/{context.project_id}")
 
 
@when(parsers.parse('I DELETE "/projects/{id}"'))
def delete_project_by_id(api, context, id):
    context.response = api.delete(f"/projects/{id}")
 
 
@when(parsers.parse('I PUT "/projects/{stored_id}" with title "{title}" and description "{description}" and active "{active}" and completed "{completed}"'))
def put_project_full(api, context, title, description, active, completed):
    context.response = api.put(f"/projects/{context.project_id}", json={
        "title": title,
        "description": description,
        "active": active == "true",     
        "completed": completed == "true",  
    })
 
 
@when(parsers.parse('I PUT "/projects/{stored_id}" with title "{title}"'))
def put_project_title_only(api, context, title):
    context.response = api.put(
        f"/projects/{context.project_id}",
        json={"title": title}
    )
 
 
@when(parsers.parse('I PUT "/projects/<id>" with title "{title}"'))
def put_project_by_id(api, context, id, title):
    context.response = api.put(f"/projects/{id}", json={"title": title})
 
 
# ==========================================
# THEN STEPS
# ==========================================
 
@then(parsers.parse('the response status should be "{status}"'))
def check_status(context, status):
    assert str(context.response.status_code) == status
 
 
@then(parsers.parse('the response should contain project title "{title}"'))
def check_project_title(context, title):
    body = context.response.json()
    # POST/PUT returns flat object; GET returns wrapped in "projects" list
    if "projects" in body:
        titles = [p["title"] for p in body["projects"]]
        assert title in titles
    else:
        assert body["title"] == title
 
 
@then(parsers.parse('the response should contain project description "{description}"'))
def check_project_description(context, description):
    body = context.response.json()
    if "projects" in body:
        descriptions = [p["description"] for p in body["projects"]]
        assert description in descriptions
    else:
        assert body["description"] == description
 
 
@then(parsers.parse('the response should contain project active status "{active}"'))
def check_project_active(context, active):
    body = context.response.json()
    if "projects" in body:
        values = [p["active"] for p in body["projects"]]
        assert active in values
    else:
        assert body["active"] == active
 
 
@then(parsers.parse('the response should contain project completed status "{completed}"'))
def check_project_completed(context, completed):
    body = context.response.json()
    if "projects" in body:
        values = [p["completed"] for p in body["projects"]]
        assert completed in values
    else:
        assert body["completed"] == completed
 
 
@then(parsers.parse('a GET request to "/projects/{stored_id}" should return "{status}"'))
def verify_project_deleted(api, context, status):
    resp = api.get(f"/projects/{context.project_id}")
    assert str(resp.status_code) == status
 
 
@then(parsers.parse('a GET request to "/projects/{stored_project_id}" should return "{status}"'))
def verify_project_gone(api, context, status):
    resp = api.get(f"/projects/{context.project_id}")
    assert str(resp.status_code) == status
 
 
@then(parsers.parse('a GET request to "/todos/{stored_todo_id}" should return "{status}"'))
def verify_todo_still_exists(api, context, status):
    resp = api.get(f"/todos/{context.todo_id}")
    assert str(resp.status_code) == status
 
 
@then("the response should contain no projects")
def check_no_projects(context):
    projects = context.response.json().get("projects", [])
    assert len(projects) == 0
 
 
@then(parsers.parse('the response should only contain projects with title "{title}"'))
def check_only_title(context, title):
    projects = context.response.json().get("projects", [])
    assert len(projects) > 0
    for p in projects:
        assert p["title"] == title
 
 
@then("the response tasks list should contain the stored todo id")
def check_tasks_contain_todo(context):
    body = context.response.json()
    projects = body.get("projects", [body])
    tasks = projects[0].get("tasks", [])
    task_ids = [t["id"] for t in tasks]
    assert context.todo_id in task_ids
 