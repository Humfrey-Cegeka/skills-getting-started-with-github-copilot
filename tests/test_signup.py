"""Tests for signup and unregister flows

Tests the core functionality:
- Successful signups
- Successful unregisters
- Error handling for invalid operations
- State persistence across multiple operations
"""

import pytest


def test_successful_signup(client, valid_email, valid_activity_name):
    """Test successful signup adds student to activity
    
    ARRANGE: Get initial participant count for an activity
    ACT: Sign up a new student for that activity
    ASSERT: Student is added to participants list and response is successful
    """
    # ARRANGE
    activity_name = valid_activity_name
    email = valid_email

    # Get initial participants
    response = client.get("/activities")
    initial_participants = response.json()[activity_name]["participants"].copy()

    # ACT
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT
    assert signup_response.status_code == 200
    assert "Signed up" in signup_response.json()["message"]
    
    # Verify student was actually added
    response = client.get("/activities")
    final_participants = response.json()[activity_name]["participants"]
    assert email in final_participants
    assert len(final_participants) == len(initial_participants) + 1


def test_successful_unregister(client, valid_activity_name):
    """Test successful unregister removes student from activity
    
    ARRANGE: Sign up a student, then unregister them
    ACT: Unregister the student
    ASSERT: Student is removed from participants list and response is successful
    """
    # ARRANGE
    activity_name = valid_activity_name
    email = "unregister.test@mergington.edu"

    # First, sign up the student
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Verify they're signed up
    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]
    initial_count = len(response.json()[activity_name]["participants"])

    # ACT: Unregister the student
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT
    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]
    
    # Verify student was actually removed
    response = client.get("/activities")
    final_participants = response.json()[activity_name]["participants"]
    assert email not in final_participants
    assert len(final_participants) == initial_count - 1


def test_unregister_nonexistent_signup(client, valid_activity_name, valid_email):
    """Test that unregistering a student not signed up fails
    
    ARRANGE: Use an email that was never signed up for the activity
    ACT: Attempt to unregister that email
    ASSERT: Returns 404 Participant not found
    """
    # ARRANGE
    activity_name = valid_activity_name
    email = "never.signed.up@mergington.edu"

    # ACT
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_unregister_from_nonexistent_activity(client, valid_email):
    """Test that unregistering from a nonexistent activity fails
    
    ARRANGE: Use an activity name that doesn't exist
    ACT: Attempt to unregister from that nonexistent activity
    ASSERT: Returns 404 Activity not found
    """
    # ARRANGE
    nonexistent_activity = "Nonexistent Club"
    email = valid_email

    # ACT
    response = client.delete(
        f"/activities/{nonexistent_activity}/signup",
        params={"email": email}
    )

    # ASSERT
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_multiple_students_signup_same_activity(client, valid_activity_name):
    """Test that multiple students can sign up for the same activity
    
    ARRANGE: Create multiple student emails
    ACT: Sign up each student for the same activity
    ASSERT: All students are added to the activity
    """
    # ARRANGE
    activity_name = valid_activity_name
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]

    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity_name]["participants"])

    # ACT: Sign up all students
    for email in students:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # ASSERT: All students are in the activity
    response = client.get("/activities")
    final_participants = response.json()[activity_name]["participants"]
    for email in students:
        assert email in final_participants
    
    assert len(final_participants) == initial_count + 3


def test_student_multiple_activities(client):
    """Test that one student can sign up for multiple different activities
    
    ARRANGE: Use one email for multiple activities
    ACT: Sign up the same student for different activities
    ASSERT: Student appears in multiple activity participant lists
    """
    # ARRANGE
    email = "multi.activity@mergington.edu"
    activities = ["Chess Club", "Programming Class", "Art Studio"]

    # ACT: Sign up for multiple activities
    for activity_name in activities:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # ASSERT: Verify student is in all activities
    response = client.get("/activities")
    all_activities = response.json()
    for activity_name in activities:
        assert email in all_activities[activity_name]["participants"]


def test_signup_and_unregister_cycles(client, valid_activity_name):
    """Test repeated signup/unregister cycles for the same student
    
    ARRANGE: Use one email and activity
    ACT: Sign up → unregister → sign up again
    ASSERT: State is correct at each step
    """
    # ARRANGE
    activity_name = valid_activity_name
    email = "cycle.test@mergington.edu"

    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity_name]["participants"])

    # ACT & ASSERT: First signup
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    response = client.get("/activities")
    assert len(response.json()[activity_name]["participants"]) == initial_count + 1

    # ACT & ASSERT: Unregister
    response2 = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    response = client.get("/activities")
    assert len(response.json()[activity_name]["participants"]) == initial_count

    # ACT & ASSERT: Sign up again
    response3 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response3.status_code == 200
    response = client.get("/activities")
    assert len(response.json()[activity_name]["participants"]) == initial_count + 1
    assert email in response.json()[activity_name]["participants"]
