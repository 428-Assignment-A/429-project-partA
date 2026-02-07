"""
Shared test fixtures for all tests
"""
import pytest
import requests

API_URL = "http://localhost:4567"

@pytest.fixture
def api():
    """API client helper"""
    class API:
        def __init__(self):
            self.url = API_URL
        
        def get(self, path):
            return requests.get(f"{self.url}{path}")
        
        def post(self, path, json=None, data=None, headers=None):
            return requests.post(f"{self.url}{path}", json=json, data=data, headers=headers)
        
        def put(self, path, json=None, data=None, headers=None):
            return requests.put(f"{self.url}{path}", json=json, data=data, headers=headers)
        
        def delete(self, path):
            return requests.delete(f"{self.url}{path}")
    
    return API()


@pytest.fixture(autouse=True)
def cleanup(api):
    """Cleanup after each test"""
    yield
    # Add cleanup code if needed
