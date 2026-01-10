import os
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock

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
from app.api.v1.deps import get_current_user
from app.api.v1.rfid import get_rfid_service
from app.main import app
from app.services.rfid_service import RFIDService
from app.models.enums import UserRole

class TestRFID(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=RFIDService)
        
        # Override dependency
        app.dependency_overrides[get_rfid_service] = lambda: self.mock_service
        
        # Default user mock (User)
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.role = UserRole.user
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_cards(self):
        self.mock_service.list_cards.return_value = [
            MagicMock(id=1, card_uid="AABBCC", owner_id=1, is_active=True, is_enabled=True, created_at="2023-01-01T00:00:00")
        ]
        
        response = self.client.get("/api/v1/rfid-cards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create_card(self):
        self.mock_service.create_card.return_value = MagicMock(
            id=1, 
            card_uid="AABBCC", 
            owner_id=1, 
            is_active=True,
            is_enabled=True,
            created_at="2023-01-01T00:00:00"
        )
        
        response = self.client.post("/api/v1/rfid-cards/", json={"card_uid": "AABBCC"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["card_uid"], "AABBCC")

    def test_create_card_too_short_uid(self):
        response = self.client.post("/api/v1/rfid-cards/", json={"card_uid": "ABC"}) # Too short (<4)
        self.assertEqual(response.status_code, 422)

    def test_get_card_detail(self):
        mock_card = MagicMock()
        mock_card.id = 1
        mock_card.card_uid = "AABBCC"
        mock_card.owner_id = 1
        mock_card.is_active = True
        mock_card.is_enabled = True
        mock_card.created_at = "2023-01-01T00:00:00"
        
        self.mock_service.get_card.return_value = mock_card
        
        response = self.client.get("/api/v1/rfid-cards/1")
        self.assertEqual(response.status_code, 200)

    def test_get_card_forbidden_not_owner(self):
        mock_card = MagicMock()
        mock_card.id = 1
        mock_card.card_uid = "XXYYZZ"
        mock_card.owner_id = 999 
        mock_card.is_active = True
        mock_card.is_enabled = True
        mock_card.created_at = "2023-01-01T00:00:00"

        self.mock_service.get_card.return_value = mock_card
        
        response = self.client.get("/api/v1/rfid-cards/1")
        self.assertEqual(response.status_code, 403)

    def test_delete_card_success(self):
        mock_card = MagicMock()
        mock_card.id = 1
        mock_card.owner_id = 1 
        mock_card.created_at = "2023-01-01T00:00:00"
        
        self.mock_service.get_card.return_value = mock_card
        self.mock_service.delete_card.return_value = True
        
        response = self.client.delete("/api/v1/rfid-cards/1")
        self.assertEqual(response.status_code, 204)

if __name__ == "__main__":
    unittest.main()
