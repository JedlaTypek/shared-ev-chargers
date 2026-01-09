import os
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# Set env vars
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("DEBUG", "True")

from fastapi.testclient import TestClient
from app.api.v1.deps import get_db
from app.main import app
from app.db.schema import User

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_db = AsyncMock()
        
        # Override get_db
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        app.dependency_overrides = {}

    @patch("app.core.security.verify_password")
    @patch("app.core.security.create_access_token")
    def test_login_success(self, mock_create_token, mock_verify):
        # Setup mocks
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.password = "hashed_secret"
        mock_user.is_active = True
        
        # db.execute returns a result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        self.mock_db.execute.return_value = mock_result
        
        mock_verify.return_value = True
        mock_create_token.return_value = "fake_token"
        
        # Send x-www-form-urlencoded data
        response = self.client.post("/api/v1/login/access-token", data={
            "username": "test@example.com",
            "password": "password"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["access_token"], "fake_token")
        self.assertEqual(data["token_type"], "bearer")

    @patch("app.core.security.verify_password")
    def test_login_invalid_credentials(self, mock_verify):
        # Setup mocks
        mock_user = MagicMock(spec=User)
        mock_user.password = "hashed_secret"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_user
        self.mock_db.execute.return_value = mock_result
        
        mock_verify.return_value = False # Wrong password
        
        response = self.client.post("/api/v1/login/access-token", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Incorrect email or password")

if __name__ == "__main__":
    unittest.main()
