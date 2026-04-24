"""Tests for activity listing endpoints

Tests the:
- GET / endpoint (redirect)
- GET /activities endpoint (activity listing)
"""

import pytest


def test_root_redirects_to_static_html(client):
    """Test that root path redirects to static HTML frontend
    
    ARRANGE: Create a TestClient
    ACT: Make GET request to /
    ASSERT: Status code is 307 (temporary redirect) and location header points to static file
    """
    # ACT
    response = client.get("/", follow_redirects=False)

    # ASSERT
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_all_activities(client):
    """Test that GET /activities returns all activities
    
    ARRANGE: Create a TestClient
    ACT: Make GET request to /activities
    ASSERT: Response contains all 9 activities
    """
    # ACT
    response = client.get("/activities")

    # ASSERT
    assert response.status_code == 200
    activities = response.json()
    
    # Verify all 9 activities are present
    assert len(activities) == 9
    expected_activities = [
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
    assert set(activities.keys()) == set(expected_activities)


def test_activity_structure(client):
    """Test that each activity has the correct structure
    
    ARRANGE: Create a TestClient
    ACT: Make GET request to /activities
    ASSERT: Each activity object has required fields
    """
    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT: Verify structure of each activity
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data, dict)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify field types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_activity_has_initial_participants(client):
    """Test that activities have initial participants
    
    ARRANGE: Create a TestClient
    ACT: Make GET request to /activities
    ASSERT: All activities have at least one participant
    """
    # ACT
    response = client.get("/activities")
    activities = response.json()

    # ASSERT
    for activity_name, activity_data in activities.items():
        assert len(activity_data["participants"]) > 0, \
            f"{activity_name} should have initial participants"


def test_chess_club_has_correct_details(client):
    """Test that Chess Club activity has expected details
    
    ARRANGE: Create a TestClient
    ACT: Make GET request to /activities
    ASSERT: Chess Club has expected description, schedule, and capacity
    """
    # ACT
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]

    # ASSERT
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]
