"""
Shared test fixtures for all tests - Updated for Backwards Compatibility and Reliability
"""
import pytest
import requests

BASE_URL = "http://localhost:4567"

def pytest_sessionstart(session):
    """
    Called before the first test runs. Checks if the API server is alive.
    """
    try:
        # Check /todos as it's a lightweight core endpoint
        requests.get(f"{BASE_URL}/gui", timeout=2)
        print(f"\n[CONFIRMED] API Server is running at {BASE_URL}")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print(f"\n[ERROR] API Server is NOT running at {BASE_URL}")
        print("Please start the .jar file before running tests.")
        pytest.exit("Server connection failed. Stopping tests.", returncode=1)

def pytest_configure(config):
    config.addinivalue_line("markers", "capability: tests that validate a specific API capability")
    config.addinivalue_line("markers", "error: tests that validate error responses (4xx/5xx)")
    config.addinivalue_line("markers", "bug: tests that document known defects")

@pytest.fixture(scope="session")
def api():
    """API client helper"""
    class API:
        def __init__(self):
            self.url = BASE_URL
        
        def get(self, path, headers=None, params=None, **kwargs):
            return requests.get(f"{self.url}{path}", headers=headers, params=params, **kwargs)
        
        def post(self, path, json=None, data=None, headers=None, **kwargs):
            return requests.post(f"{self.url}{path}", json=json, data=data, headers=headers, **kwargs)
        
        def put(self, path, json=None, data=None, headers=None, **kwargs):
            return requests.put(f"{self.url}{path}", json=json, data=data, headers=headers, **kwargs)
        
        def delete(self, path, headers=None, params=None, **kwargs):
            return requests.delete(f"{self.url}{path}", headers=headers, params=params, **kwargs)

        def head(self, path, headers=None, **kwargs):
            return requests.head(f"{self.url}{path}", headers=headers, **kwargs)

        def options(self, path, headers=None, **kwargs):
            return requests.options(f"{self.url}{path}", headers=headers, **kwargs)
        
    return API()

@pytest.fixture(autouse=True)
def cleanup(api):
    # --- SETUP: Record state before test ---
    # (Optional: you could record the number of items)
    
    yield # The test runs here
    
    # --- TEARDOWN: Wipe the data ---
    # This ensures that even if a test fails halfway, 
    # the next test starts with a clean list.
    todos_resp = api.get("/todos")
    if todos_resp.status_code == 200:
        todos = todos_resp.json().get("todos", [])
        for item in todos:
            api.delete(f"/todos/{item['id']}")


def pytest_report_teststatus(report, config):
    """
    This hook runs when a test finishes. 
    It modifies the terminal output to include the markers.
    """
    if report.when == 'call':
        # Get the markers from the test item
        # Note: This requires a slightly more complex approach if 
        # using 'report', but for a simple print, we use item collected.
        pass

def pytest_itemcollected(item):
    """
    This modifies the 'Node ID' (the name in the terminal) 
    to include markers as soon as the test is found.
    """
    # Get all custom marker names
    markers = [mark.name for mark in item.iter_markers()]
    if markers:
        # Appends [marker1, marker2] to the end of the test name
        item._nodeid = f"{item.nodeid} \033[93m[{', '.join(markers)}]\033[0m"


import random
from collections import defaultdict

def pytest_collection_modifyitems(config, items):
    random.seed(config.getoption("--randomly-seed", default=0))

    buckets = defaultdict(list)
    for item in items:
        buckets[item.fspath].append(item)

    shuffled = []
    files = list(buckets.keys())
    random.shuffle(files)

    while files:
        for f in files[:]:
            if buckets[f]:
                shuffled.append(buckets[f].pop(0))
            else:
                files.remove(f)

    items[:] = shuffled



@pytest.fixture(autouse=True)
def ensure_server_alive():
    """Verify that the API server is running before each test; abort all tests if down."""
    try:
        resp = requests.get(f"{BASE_URL}/gui", timeout=2)
        if resp.status_code >= 500:
            pytest.exit(f"API Server returned {resp.status_code} at {BASE_URL}.", returncode=1)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.exit(f"API server connection cannot be established at {BASE_URL}.", returncode=1)