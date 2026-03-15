import pytest
import requests
from typing import Dict, List, Optional, Any, Union

class TodoAPI:
    def __init__(self, base_url: str = "http://localhost:4567"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return self.session.request(method, url, **kwargs)

    # --- BDD Methods ---
    def get_todos(self, params=None) -> requests.Response:
        return self._make_request("GET", "/todos", params=params)

    def create_todo(self, payload: Any, content_type: str = "application/json") -> requests.Response:
        headers = {"Content-Type": content_type}
        if content_type == "application/xml" and isinstance(payload, str):
            return self._make_request("POST", "/todos", data=payload, headers=headers)
        return self._make_request("POST", "/todos", json=payload, headers=headers)

    def get_todo(self, todo_id, accept="application/json") -> requests.Response:
        return self._make_request("GET", f"/todos/{todo_id}", headers={"Accept": accept})

    def delete_todo(self, todo_id) -> requests.Response:
        return self._make_request("DELETE", f"/todos/{todo_id}")

    # --- COMPATIBILITY ALIASES for outer conftest.py ---
    # These prevent the 'AttributeError: TodoAPI has no attribute get' errors
    def get(self, path, **kwargs): return self._make_request("GET", path, **kwargs)
    def post(self, path, **kwargs): return self._make_request("POST", path, **kwargs)
    def put(self, path, **kwargs): return self._make_request("PUT", path, **kwargs)
    def delete(self, path, **kwargs): return self._make_request("DELETE", path, **kwargs)
    def head(self, path, **kwargs): return self._make_request("HEAD", path, **kwargs)
    def options(self, path, **kwargs): return self._make_request("OPTIONS", path, **kwargs)

@pytest.fixture
def api():
    return TodoAPI()