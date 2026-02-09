"""
Category-specific test fixtures.
Cleans up categories after each test to ensure test independence.
"""
import pytest
import requests

BASE_URL = "http://localhost:4567"


def pytest_runtest_setup(item):
    """
    Called before every individual test. Terminates the session if the API server is not running.
    """
    try:
        requests.get(f"{BASE_URL}/todos", timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.exit("API Server is not running. Terminating tests.", returncode=1)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Runs after each test phase (setup, call, teardown).
    If a ConnectionError caused the failure, terminate immediately.
    """
    outcome = yield
    report = outcome.get_result()
    if report.failed and call.excinfo is not None:
        if call.excinfo.errisinstance((requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            pytest.exit("API Server connection lost. Terminating tests.", returncode=1)


@pytest.fixture(autouse=True)
def cleanup_categories(api):
    yield
    # Teardown: Remove all categories created during the test
    categories_resp = api.get("/categories")
    if categories_resp.status_code == 200:
        categories = categories_resp.json().get("categories", [])
        for item in categories:
            api.delete(f"/categories/{item['id']}")
