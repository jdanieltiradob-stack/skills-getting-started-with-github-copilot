"""Tests for the signup endpoint (POST /activities/{activity_name}/signup)"""

import pytest
from fastapi.testclient import TestClient
import copy
from src.app import app, activities as original_activities_data


@pytest.fixture
def client():
    """Provide a test client with a fresh copy of activities for each test"""
    # Store original activities
    from src import app as app_module
    original_activities = copy.deepcopy(original_activities_data)
    
    # Reset activities for this test
    app_module.activities = copy.deepcopy(original_activities)
    
    client = TestClient(app)
    
    yield client
    
    # Restore original activities after test
    app_module.activities = original_activities


def test_signup_successful(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_adds_participant_to_list(client):
    """Test that signup actually adds the participant to the activity"""
    email = "test@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client):
    """Test that signing up for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up(client):
    """Test that signing up twice with same email returns 400"""
    email = "michael@mergington.edu"  # Already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_increases_participant_count(client):
    """Test that signup increases the participant count for an activity"""
    # Get initial count
    initial_response = client.get("/activities")
    initial_activities = initial_response.json()
    initial_count = len(initial_activities["Programming Class"]["participants"])
    
    # Sign up new participant
    email = "newprogrammer@mergington.edu"
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify count increased
    updated_response = client.get("/activities")
    updated_activities = updated_response.json()
    final_count = len(updated_activities["Programming Class"]["participants"])
    assert final_count == initial_count + 1


def test_signup_at_max_capacity(client):
    """Test that signup fails when activity is at max capacity"""
    # Find an activity that's close to max capacity, or modify one for testing
    # Chess Club has max 12, currently has 2 participants
    activity_name = "Chess Club"
    
    # Fill up the activity to max capacity
    activities = client.get("/activities").json()
    current_count = len(activities[activity_name]["participants"])
    max_count = activities[activity_name]["max_participants"]
    
    # Add participants until at capacity
    students_to_add = max_count - current_count
    for i in range(students_to_add):
        email = f"filler{i}@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200, f"Failed to add student {i} to reach capacity"
    
    # Verify we're at capacity
    activities = client.get("/activities").json()
    assert len(activities[activity_name]["participants"]) == max_count
    
    # Try to signup one more (should fail)
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overbooking@mergington.edu"}
    )
    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower() or \
           "full" in response.json()["detail"].lower() or \
           "max" in response.json()["detail"].lower()


def test_signup_missing_email_parameter(client):
    """Test that signup without email parameter returns error"""
    response = client.post("/activities/Chess Club/signup")
    assert response.status_code == 422  # Unprocessable Entity


def test_signup_empty_email(client):
    """Test that signup with empty email is handled"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": ""}
    )
    # FastAPI will either accept it or reject it; we're testing the behavior
    # Empty email could be valid from API perspective but shouldn't match existing participants
    assert response.status_code in [200, 422]
