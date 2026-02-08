"""
Category-specific test fixtures.
Cleans up categories after each test to ensure test independence.
"""
import pytest


@pytest.fixture(autouse=True)
def cleanup_categories(api):
    yield
    # Teardown: Remove all categories created during the test
    categories_resp = api.get("/categories")
    if categories_resp.status_code == 200:
        categories = categories_resp.json().get("categories", [])
        for item in categories:
            api.delete(f"/categories/{item['id']}")
