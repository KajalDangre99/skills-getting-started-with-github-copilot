import pytest


def test_get_activities(client):
    """Test that we can fetch all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) > 0


def test_activity_structure(client):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_details in activities.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    email = "test@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity in result["message"]


def test_signup_duplicate_participant(client):
    """Test that a participant cannot sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    activity = "Chess Club"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    email = "unregister@mergington.edu"
    activity = "Programming Class"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Then unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert unregister_response.status_code == 200
    result = unregister_response.json()
    assert email in result["message"]
    
    # Verify participant is removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_not_registered_participant(client):
    """Test unregistering a participant who is not registered"""
    email = "notregistered@mergington.edu"
    activity = "Tennis Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_participant_count_after_signup(client):
    """Test that participant count is correctly updated after signup"""
    email = "counter@mergington.edu"
    activity = "Gym Class"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Get updated participant count
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity]["participants"])
    
    assert updated_count == initial_count + 1


def test_participant_count_after_unregister(client):
    """Test that participant count is correctly updated after unregister"""
    email = "uncounter@mergington.edu"
    activity = "Basketball Team"
    
    # Sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Get participant count after signup
    after_signup = client.get("/activities")
    count_after_signup = len(after_signup.json()[activity]["participants"])
    
    # Unregister
    client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Get participant count after unregister
    after_unregister = client.get("/activities")
    count_after_unregister = len(after_unregister.json()[activity]["participants"])
    
    assert count_after_unregister == count_after_signup - 1
