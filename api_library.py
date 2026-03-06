import requests
from typing import Dict, List, Optional, Any, Union

class TodoAPI:
    """
    Clean Code wrapper for Todo Manager REST API calls.
    Returns full requests.Response objects to allow BDD steps to verify 
    status codes, headers, and body content.
    """

    def __init__(self, base_url: str = "http://localhost:4567"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Internal helper to execute requests."""
        url = f"{self.base_url}{endpoint}"
        # We do NOT use raise_for_status() because we need to test 400/404/405 flows
        return self.session.request(method, url, **kwargs)

    # --- Collection Methods ---

    def get_todos(self, params: Optional[Dict] = None) -> requests.Response:
        """GET /todos - supports filtering via params (e.g. {'title': 'task'})"""
        return self._make_request("GET", "/todos", params=params)

    def create_todo(self, payload: Dict[str, Any], content_type: str = "application/json") -> requests.Response:
        """POST /todos - Create a new todo with flexible payload and headers."""
        headers = {"Content-Type": content_type}
        
        # Handle XML strings vs JSON dicts
        if content_type == "application/xml" and isinstance(payload, str):
            return self._make_request("POST", "/todos", data=payload, headers=headers)
        return self._make_request("POST", "/todos", json=payload, headers=headers)

    def options_todos(self, endpoint: str = "/todos") -> requests.Response:
        """OPTIONS request for discovery testing."""
        return self._make_request("OPTIONS", endpoint)

    def head_todos(self, endpoint: str = "/todos") -> requests.Response:
        """HEAD request for metadata testing."""
        return self._make_request("HEAD", endpoint)

    # --- Instance Methods (:id) ---

    def get_todo(self, todo_id: Union[int, str], accept: str = "application/json") -> requests.Response:
        """GET /todos/:id - Supports custom Accept headers for format testing."""
        headers = {"Accept": accept}
        return self._make_request("GET", f"/todos/{todo_id}", headers=headers)

    def update_todo_post(self, todo_id: Union[int, str], payload: Dict) -> requests.Response:
        """POST /todos/:id - Partial update (or toggle doneStatus)."""
        return self._make_request("POST", f"/todos/{todo_id}", json=payload)

    def update_todo_put(self, todo_id: Union[int, str], payload: Dict) -> requests.Response:
        """PUT /todos/:id - Full replacement."""
        return self._make_request("PUT", f"/todos/{todo_id}", json=payload)

    def delete_todo(self, todo_id: Union[int, str], accept: str = "application/json") -> requests.Response:
        """DELETE /todos/:id"""
        headers = {"Accept": accept}
        return self._make_request("DELETE", f"/todos/{todo_id}", headers=headers)

    # --- Extra Utilities ---

    def get_categories(self) -> requests.Response:
        return self._make_request("GET", "/categories")

    def get_projects(self) -> requests.Response:
        return self._make_request("GET", "/projects")