import os
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock

# Set env vars BEFORE importing app modules
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("DEBUG", "True")

from fastapi.testclient import TestClient
from app.api.v1.user import get_user_service
from app.main import app
from app.services.user_service import UserService
from app.models.enums import UserRole
from app.api.v1.deps import get_current_user

class TestUser(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=UserService)
        
        # Override dependency
        app.dependency_overrides[get_user_service] = lambda: self.mock_service
        
        # Mock current user (default to admin to allow reading everything)
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.role = UserRole.admin
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_create_user(self):
        # Setup mock return value
        self.mock_service.create_user.return_value = {
            "id": 2,
            "name": "Test User",
            "email": "new@example.com",
            "role": "user",
            "balance": 0.0,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.post("/api/v1/users/", json={
            "name": "Test User",
            "email": "new@example.com",
            "password": "password123"
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Test User")
        self.assertEqual(data["id"], 2)

    def test_get_user(self):
        # Setup mock
        self.mock_service.get_user.return_value = {
            "id": 2,
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
            "balance": 0.0,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.get("/api/v1/users/2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 2)

    def test_update_user_password_success(self):
        # Mocking successful update
        self.mock_service.update_user.return_value = {
            "id": 1,
            "name": "Updated",
            "email": "test@example.com",
            "role": "admin",
            "balance": 0.0,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.patch("/api/v1/users/1", json={
            "password": "newpassword",
            "old_password": "correct_old"
        })
        self.assertEqual(response.status_code, 200)

    def test_update_user_password_missing_old(self):
        # Mock service raising ValueError (replicates invalid old password)
        self.mock_service.update_user.side_effect = ValueError("Incorrect old password")
        
        response = self.client.patch("/api/v1/users/1", json={
            "password": "newpassword",
            "old_password": "wrong"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Incorrect old password", response.json()["detail"])
        
        self.mock_service.update_user.side_effect = None # Reset

    def test_update_role_forbidden(self):
        # Downgrade current user to User
        self.mock_user.role = UserRole.user
        self.mock_user.id = 1
        
        response = self.client.patch("/api/v1/users/1", json={
            "role": "admin"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("Cannot set role to admin", response.json()["detail"])

    def test_update_role_allowed(self):
        # User changing to Owner is allowed
        self.mock_user.role = UserRole.user
        self.mock_user.id = 1
        
        self.mock_service.update_user.return_value = {
            "id": 1, 
            "role": "owner",
            "name": "Test User",
            "email": "test@example.com",
            "balance": 0.0,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.patch("/api/v1/users/1", json={
            "role": "owner"
        })
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
