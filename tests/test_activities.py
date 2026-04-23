"""Tests for the activities endpoint (GET /activities)"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Verify expected activities are present
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Basketball Team" in activities
    assert "Soccer Club" in activities
    assert "Art Club" in activities
    assert "Drama Club" in activities
    assert "Debate Club" in activities
    assert "Science Club" in activities


def test_activity_has_required_fields(client):
    """Test that each activity has all required fields"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"


def test_activity_participants_is_list(client):
    """Test that participants field is a list"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list), \
            f"Activity '{activity_name}' participants is not a list"


def test_activity_max_participants_is_positive(client):
    """Test that max_participants is a positive integer"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["max_participants"], int), \
            f"Activity '{activity_name}' max_participants is not an integer"
        assert activity_data["max_participants"] > 0, \
            f"Activity '{activity_name}' max_participants is not positive"
