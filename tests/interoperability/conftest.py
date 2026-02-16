"""
Interoperability-specific test fixtures.
Cleans up all entities (todos, projects, categories) and their relationships
after each test to ensure test independence.
"""
import pytest


@pytest.fixture(autouse=True)
def cleanup_interoperability(api):
    """Clean up todos, projects, and categories after each interoperability test."""
    yield
    
    # Cleanup todos
    todos_resp = api.get("/todos")
    if todos_resp.status_code == 200:
        for todo in todos_resp.json().get("todos", []):
            todo_id = todo.get("id")
            if todo_id is not None:
                api.delete(f"/todos/{todo_id}")
    
    # Cleanup projects
    projects_resp = api.get("/projects")
    if projects_resp.status_code == 200:
        for project in projects_resp.json().get("projects", []):
            project_id = project.get("id")
            if project_id is not None:
                api.delete(f"/projects/{project_id}")
    
    # Cleanup categories
    categories_resp = api.get("/categories")
    if categories_resp.status_code == 200:
        for category in categories_resp.json().get("categories", []):
            category_id = category.get("id")
            if category_id is not None:
                api.delete(f"/categories/{category_id}")
