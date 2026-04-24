"""Pytest configuration and fixtures for the API test suite

Provides:
- TestClient fixture for making requests to the FastAPI app
- Fresh app state for each test (no state leakage between tests)
- Sample data fixtures for testing
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the API
    
    Returns a fresh TestClient for each test, ensuring test isolation.
    """
    return TestClient(app)


@pytest.fixture
def valid_email():
    """Sample valid email for testing"""
    return "test.student@mergington.edu"


@pytest.fixture
def valid_activity_name():
    """Sample valid activity name for testing"""
    return "Chess Club"


@pytest.fixture
def invalid_email_formats():
    """Collection of invalid email formats for testing validation"""
    return [
        "",                    # Empty string
        "invalid_email",       # Missing @
        "@example.com",        # Missing local part
        "user@",               # Missing domain
        "user@domain",         # Missing TLD
        "user name@domain.com", # Space in local part
        "user@dom ain.com",    # Space in domain
    ]


@pytest.fixture
def all_activities():
    """List of all valid activity names in the system"""
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Studio",
        "Music Band",
        "Debate Club",
        "Science Club"
    ]
