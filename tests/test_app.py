import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities database before each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns the activity list."""
    # Arrange: No special setup needed, activities are pre-loaded

    # Act: Make the GET request
    response = client.get("/activities")

    # Assert: Check status and response content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange: Choose an activity and email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make the POST request
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success response and that participant was added
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was added to the activity
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate():
    """Test that duplicate signup is rejected."""
    # Arrange: Sign up a student first
    activity_name = "Programming Class"
    email = "test@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up the same student again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check that it's rejected with 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_remove_participant_success():
    """Test successful removal of a participant."""
    # Arrange: Add a participant first
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Remove the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: Check success and that participant was removed
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_remove_participant_not_found():
    """Test removing a non-existent participant."""
    # Arrange: Activity and email that doesn't exist
    activity_name = "Art Club"
    email = "nonexistent@mergington.edu"

    # Act: Try to remove the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: Check that it's rejected with 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]