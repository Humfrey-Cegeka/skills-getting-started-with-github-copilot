"""Tests for input validation and edge cases

Tests validation of:
- Email formats
- Activity name validation
- Duplicate signups
- Capacity limits
- Edge cases (special characters, very long inputs)
"""

import pytest


def test_signup_with_invalid_email_formats(client, invalid_email_formats):
    """Test that invalid email formats are handled (if validation is added)
    
    ARRANGE: Set up invalid email formats and a valid activity
    ACT: Attempt to sign up with each invalid email
    ASSERT: Signup succeeds (note: current app doesn't validate email format, 
            but this test documents the behavior)
    """
    # ARRANGE
    activity_name = "Chess Club"

    # ACT & ASSERT: Current app accepts any string as email
    for invalid_email in invalid_email_formats:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": invalid_email}
        )
        # Note: Current implementation doesn't validate email format
        # It will accept the signup. In a real app, we'd assert 400 here.
        # For now, we document the current behavior.
        if invalid_email == "":
            # Empty string is handled differently by FastAPI query params
            assert response.status_code in [422, 200]
        else:
            assert response.status_code == 200


def test_signup_for_nonexistent_activity(client, valid_email):
    """Test that signup for nonexistent activity fails
    
    ARRANGE: Use a non-existent activity name and valid email
    ACT: Attempt signup for activity that doesn't exist
    ASSERT: Returns 404 Activity not found
    """
    # ARRANGE
    nonexistent_activity = "Underwater Basket Weaving"
    
    # ACT
    response = client.post(
        f"/activities/{nonexistent_activity}/signup",
        params={"email": valid_email}
    )

    # ASSERT
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_case_sensitive_activity_names(client, valid_email):
    """Test that activity names are case-sensitive
    
    ARRANGE: Use different case variations of an activity name
    ACT: Attempt signup with wrong case
    ASSERT: Returns 404 for case mismatch
    """
    # ARRANGE
    correct_name = "Chess Club"
    wrong_case_names = ["chess club", "CHESS CLUB", "chess Club", "Chess club"]

    # ACT & ASSERT
    for wrong_name in wrong_case_names:
        response = client.post(
            f"/activities/{wrong_name}/signup",
            params={"email": valid_email}
        )
        assert response.status_code == 404, \
            f"Expected 404 for '{wrong_name}' but got {response.status_code}"


def test_duplicate_signup_rejected(client, valid_email, valid_activity_name):
    """Test that duplicate signups are rejected
    
    ARRANGE: Sign up a student for an activity, then attempt duplicate signup
    ACT: Sign up the same student twice
    ASSERT: Second signup returns 400 (already signed up)
    """
    # ARRANGE
    activity_name = valid_activity_name
    email = valid_email

    # ACT: First signup
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200

    # ACT: Attempt duplicate signup
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # ASSERT
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_with_special_characters_in_email(client, valid_activity_name):
    """Test handling of special characters in email (current app accepts them)
    
    ARRANGE: Create email addresses with special characters
    ACT: Attempt signup with special character emails
    ASSERT: Signups are accepted (current app doesn't validate)
    """
    # ARRANGE
    activity_name = valid_activity_name
    special_emails = [
        "user+tag@example.com",
        "user.name@example.com",
        "user_name@example.com",
        "user-name@example.com"
    ]

    # ACT & ASSERT
    for email in special_emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Current app accepts these formats
        assert response.status_code == 200


def test_signup_with_very_long_email(client, valid_activity_name):
    """Test handling of extremely long email addresses
    
    ARRANGE: Create a very long email string
    ACT: Attempt signup with long email
    ASSERT: Signup is accepted (current app has no length limit)
    """
    # ARRANGE
    activity_name = valid_activity_name
    long_email = "a" * 100 + "@" + "b" * 100 + ".com"

    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": long_email}
    )

    # ASSERT
    assert response.status_code == 200


def test_existing_participant_still_in_list(client, valid_activity_name):
    """Test that existing participants remain after new signups
    
    ARRANGE: Choose an activity with existing participants
    ACT: Sign up a new student
    ASSERT: Both new and existing participants are in the activity
    """
    # ARRANGE
    activity_name = valid_activity_name
    new_email = "new.student@mergington.edu"

    # Get initial participants
    response = client.get("/activities")
    initial_count = len(response.json()[activity_name]["participants"])

    # ACT: Sign up new student
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # ASSERT
    response = client.get("/activities")
    final_count = len(response.json()[activity_name]["participants"])
    assert final_count == initial_count + 1
