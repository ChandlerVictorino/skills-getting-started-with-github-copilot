"""
Tests for the High School Management System API
Uses the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Provide a test client for API requests"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to original state before each test"""
    # Arrange: Save original state
    original = copy.deepcopy(activities)
    yield
    # Cleanup: Restore after test
    activities.clear()
    activities.update(original)


# ============ GET /activities Tests ============
class TestGetActivities:
    """Tests for retrieving all activities"""
    
    def test_get_activities_returns_success(self, client, reset_activities):
        """GET /activities returns 200 with all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Each activity has required fields: description, schedule, max_participants, participants"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_data in activities_data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
            assert isinstance(activity_data["participants"], list)


# ============ POST /activities/{name}/signup Tests ============
class TestSignup:
    """Tests for signing up for an activity"""
    
    def test_signup_new_student_success(self, client, reset_activities):
        """A new student successfully signs up for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        assert f"Signed up {email}" in response.json()["message"]
    
    def test_signup_duplicate_fails(self, client, reset_activities):
        """Attempting a duplicate signup returns 400 error"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Signing up for non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Club 2000"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_multiple_different_students(self, client, reset_activities):
        """Multiple different students can sign up for the same activity"""
        # Arrange
        activity = "Tennis Club"
        new_emails = ["student1@mergington.edu", "student2@mergington.edu"]
        initial_count = len(activities[activity]["participants"])
        
        # Act
        for email in new_emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        assert len(activities[activity]["participants"]) == initial_count + len(new_emails)
        for email in new_emails:
            assert email in activities[activity]["participants"]


# ============ DELETE /activities/{name}/signup Tests ============
class TestUnregister:
    """Tests for unregistering from an activity"""
    
    def test_unregister_existing_student_success(self, client, reset_activities):
        """A registered student successfully unregisters"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        assert email in activities[activity]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        assert f"Unregistered {email}" in response.json()["message"]
    
    def test_unregister_not_signed_up_fails(self, client, reset_activities):
        """Unregistering a student not signed up returns 400"""
        # Arrange
        email = "notstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Unregistering from non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


# ============ GET / (Root) Tests ============
class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Root path redirects to static index.html"""
        # Arrange (none needed)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
