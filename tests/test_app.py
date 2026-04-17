import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Test client fixture
@pytest.fixture
def client():
    return TestClient(app)

# Fixture to reset activities data before each test
@pytest.fixture(autouse=True)
def reset_activities():
    # Store original data
    original_activities = activities.copy()
    yield
    # Reset after test
    activities.clear()
    activities.update(original_activities)

def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity

def test_signup_success(client):
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    # Verify added to participants
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]

def test_signup_duplicate(client):
    # First signup
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity(client):
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success(client):
    # First signup
    client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Chess%20Club/participants/test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    # Verify removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" not in activities_data["Chess Club"]["participants"]

def test_unregister_not_enrolled(client):
    response = client.delete("/activities/Chess%20Club/participants/nonexistent@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity(client):
    response = client.delete("/activities/NonExistent/participants/test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]