"""Tests for the remove participant endpoint (DELETE /activities/{activity_name}/participants)"""

import pytest
from fastapi.testclient import TestClient
import copy
from src import app as app_module


@pytest.fixture
def client():
    """Provide a test client with a fresh copy of activities for each test"""
    # Store original activities
    original_activities = copy.deepcopy(app_module.app.activities)
    
    # Reset activities for this test
    app_module.app.activities = copy.deepcopy(original_activities)
    
    client = TestClient(app_module.app)
    
    yield client
    
    # Restore original activities after test
    app_module.app.activities = original_activities


def test_remove_participant_successful(client):
    """Test successfully removing a participant from an activity"""
    email = "michael@mergington.edu"  # In Chess Club
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    assert email in response.json()["message"]


def test_remove_participant_from_list(client):
    """Test that removal actually removes the participant from the activity"""
    email = "michael@mergington.edu"  # In Chess Club
    
    # Verify participant is in list before removal
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    
    # Remove participant
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant is removed from list
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_activity_not_found(client):
    """Test that removing from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent Club/participants",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_not_found(client):
    """Test that removing non-existent participant returns 404"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_remove_participant_decreases_count(client):
    """Test that removal decreases the participant count"""
    email = "michael@mergington.edu"
    
    # Get initial count
    initial_response = client.get("/activities")
    initial_activities = initial_response.json()
    initial_count = len(initial_activities["Chess Club"]["participants"])
    
    # Remove participant
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify count decreased
    updated_response = client.get("/activities")
    updated_activities = updated_response.json()
    final_count = len(updated_activities["Chess Club"]["participants"])
    assert final_count == initial_count - 1


def test_remove_participant_cannot_remove_twice(client):
    """Test that removing the same participant twice fails on second attempt"""
    email = "michael@mergington.edu"
    
    # First removal should succeed
    response1 = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second removal should fail
    response2 = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response2.status_code == 404
    assert "Participant not found" in response2.json()["detail"]


def test_remove_participant_missing_email_parameter(client):
    """Test that remove without email parameter returns error"""
    response = client.delete("/activities/Chess Club/participants")
    assert response.status_code == 422  # Unprocessable Entity


def test_remove_different_participant_from_same_activity(client):
    """Test removing one participant doesn't affect others in same activity"""
    # Chess Club has michael@mergington.edu and daniel@mergington.edu
    email_to_remove = "michael@mergington.edu"
    email_remaining = "daniel@mergington.edu"
    
    # Remove one participant
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email_to_remove}
    )
    assert response.status_code == 200
    
    # Verify removed participant is gone
    activities = client.get("/activities").json()
    assert email_to_remove not in activities["Chess Club"]["participants"]
    
    # Verify other participant is still there
    assert email_remaining in activities["Chess Club"]["participants"]
