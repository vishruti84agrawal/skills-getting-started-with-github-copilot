"""Tests for the High School Management System API"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture for FastAPI TestClient"""
    return TestClient(app)


# ==================== GET /activities Tests ====================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    # Arrange & Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_get_activities_has_correct_structure(client):
    """Test that activities have the correct data structure"""
    # Arrange & Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_get_activities_participants_are_strings(client):
    """Test that participants in activities are email strings"""
    # Arrange & Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, details in activities.items():
        for participant in details["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant


# ==================== POST /activities/{activity_name}/signup Tests ====================

def test_signup_successful(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_duplicate_returns_400(client):
    """Test that signing up twice returns 400 error"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity_returns_404(client):
    """Test that signing up for non-existent activity returns 404"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds the participant to the activity"""
    # Arrange
    activity_name = "Tennis Club"
    email = "test.student@mergington.edu"
    
    # Act - signup
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Act - fetch activities
    activities_response = client.get("/activities")
    
    # Assert
    assert signup_response.status_code == 200
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


# ==================== DELETE /activities/{activity_name}/unregister Tests ====================

def test_unregister_successful(client):
    """Test successful unregistration from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert "Unregistered" in data["message"]


def test_unregister_nonexistent_participant_returns_400(client):
    """Test that unregistering non-existent participant returns 400"""
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_unregister_nonexistent_activity_returns_404(client):
    """Test that unregistering from non-existent activity returns 404"""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_removes_participant_from_activity(client):
    """Test that unregister actually removes the participant from the activity"""
    # Arrange
    activity_name = "Art Studio"
    email = "maya@mergington.edu"  # Already registered
    
    # Act - verify initial state
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"]
    
    # Act - unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Act - verify final state
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity_name]["participants"]
    
    # Assert
    assert unregister_response.status_code == 200
    assert email in initial_participants
    assert email not in final_participants


# ==================== Integration Tests ====================

def test_signup_then_unregister_flow(client):
    """Test the complete flow of signing up and then unregistering"""
    # Arrange
    activity_name = "Debate Team"
    email = "integration.test@mergington.edu"
    
    # Act - signup
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Verify signup worked
    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]
    
    # Act - unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    assert unregister_response.status_code == 200
    
    # Assert - verify unregister worked
    activities_after_unregister = client.get("/activities").json()
    assert email not in activities_after_unregister[activity_name]["participants"]
