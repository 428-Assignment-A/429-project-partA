#!/usr/bin/env python3
"""
BDD Test Setup Script for Todo Manager REST API

This script creates the BDD_tests directory structure and initializes
empty files for pytest-bdd testing following Clean Code principles.

Usage: python setup_bdd_tests.py
"""

import os
import sys

def create_directory_structure():
    """Create the BDD_tests directory structure."""
    directories = [
        "BDD_tests",
        "BDD_tests/features",
        "BDD_tests/step_definitions"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_feature_files():
    """Create empty .feature files with basic template for todo_creation."""
    feature_files = [
        "BDD_tests/features/todo_creation.feature",
        "BDD_tests/features/todo_update.feature",
        "BDD_tests/features/todo_completion.feature",
        "BDD_tests/features/todo_deletion.feature",
        "BDD_tests/features/todo_searching.feature"
    ]

    # Basic Scenario Outline template for todo_creation.feature
    todo_creation_content = """Feature: Todo Creation
  As a user of the Todo Manager API
  I want to create new todos
  So that I can track my tasks

  Background:
    Given the API is running

  Scenario Outline: Create a new todo with valid data
    When I create a todo with title "<title>" and description "<description>"
    Then the response status should be 201
    And the todo should be created with the provided details

    Examples:
      | title          | description          |
      | Buy groceries  | Milk, bread, eggs    |
      | Call dentist   | Schedule appointment  |
      | Write report   | Q4 financial report   |
"""

    for file_path in feature_files:
        if file_path.endswith("todo_creation.feature"):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(todo_creation_content)
        else:
            # Create empty files for other features
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")  # Empty file
        print(f"Created file: {file_path}")

def create_step_definition_files():
    """Create step definition files."""
    step_files = [
        "BDD_tests/step_definitions/test_todo_steps.py",
        "BDD_tests/step_definitions/conftest.py"
    ]

    # Content for conftest.py with API check fixture
    conftest_content = '''import pytest
import requests
from api_library import TodoAPI

@pytest.fixture(scope="session")
def api_client():
    """Fixture to provide a configured API client."""
    return TodoAPI(base_url="http://localhost:4567")

@pytest.fixture(scope="function", autouse=True)
def reset_state(api_client):
    """Reset the system state before and after each scenario."""
    # Code to run BEFORE each scenario
    # You can add any pre-test setup here
    yield
    # Code to run AFTER each scenario to restore the system
    # Since it's an in-memory API, you might need to delete
    # the specific IDs you created during the test
    # Example: api_client.delete_all_todos()

@pytest.fixture(scope="session", autouse=True)
def check_api_running():
    """Check if the API is running before starting tests."""
    try:
        response = requests.get("http://localhost:4567", timeout=5)
        if response.status_code not in [200, 404]:  # 404 is acceptable for root endpoint
            pytest.fail("API is not responding correctly")
    except requests.exceptions.RequestException:
        pytest.fail("API is not running at http://localhost:4567")
'''

    for file_path in step_files:
        if file_path.endswith("conftest.py"):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(conftest_content)
        else:
            # Create empty test_todo_steps.py
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")  # Empty file
        print(f"Created file: {file_path}")

def create_api_library():
    """Create the API library wrapper."""
    api_library_content = '''import requests
from typing import Dict, List, Optional, Any

class TodoAPI:
    """
    Clean Code wrapper for Todo Manager REST API calls.

    This class encapsulates all API interactions following Single Responsibility
    Principle and provides a clean interface for BDD step definitions.
    """

    def __init__(self, base_url: str = "http://localhost:4567"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the Todo Manager API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_todos(self) -> List[Dict[str, Any]]:
        """Get all todos."""
        response = self._make_request("GET", "/todos")
        return response.json().get("todos", [])

    def get_todo(self, todo_id: int) -> Dict[str, Any]:
        """Get a specific todo by ID."""
        response = self._make_request("GET", f"/todos/{todo_id}")
        return response.json()

    def create_todo(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new todo.

        Args:
            title: Todo title
            description: Optional todo description

        Returns:
            Created todo data
        """
        data = {"title": title}
        if description:
            data["description"] = description

        response = self._make_request("POST", "/todos", json=data)
        return response.json()

    def update_todo(self, todo_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update an existing todo.

        Args:
            todo_id: ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            completed: Completion status (optional)

        Returns:
            Updated todo data
        """
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if completed is not None:
            data["completed"] = completed

        response = self._make_request("PUT", f"/todos/{todo_id}", json=data)
        return response.json()

    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete a todo.

        Args:
            todo_id: ID of the todo to delete

        Returns:
            True if deletion was successful
        """
        self._make_request("DELETE", f"/todos/{todo_id}")
        return True

    def search_todos(self, query: str) -> List[Dict[str, Any]]:
        """
        Search todos by title or description.

        Args:
            query: Search query string

        Returns:
            List of matching todos
        """
        # Assuming the API supports search via query parameter
        response = self._make_request("GET", "/todos", params={"q": query})
        return response.json().get("todos", [])

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        response = self._make_request("GET", "/categories")
        return response.json().get("categories", [])

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        response = self._make_request("GET", "/projects")
        return response.json().get("projects", [])
'''

    file_path = "api_library.py"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(api_library_content)
    print(f"Created file: {file_path}")

def main():
    """Main function to set up BDD test structure."""
    print("Setting up BDD test structure for Todo Manager API...")

    try:
        create_directory_structure()
        create_feature_files()
        create_step_definition_files()
        create_api_library()

        print("\nBDD test structure setup complete!")
        print("\nNext steps:")
        print("1. Install pytest-bdd: pip install pytest-bdd")
        print("2. Start your API server on http://localhost:4567")
        print("3. Run BDD tests: pytest BDD_tests/")
        print("4. Implement step definitions in test_todo_steps.py")

    except Exception as e:
        print(f"Error setting up BDD tests: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()