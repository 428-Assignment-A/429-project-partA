import pytest

@pytest.fixture(autouse=True)
def cleanup_projects(api):
    yield
    resp = api.get("/projects")
    if resp.status_code != 200:
        return
    for p in resp.json().get("projects", []):
        pid = p.get("id")
        if pid is not None:
            api.delete(f"/projects/{pid}")
