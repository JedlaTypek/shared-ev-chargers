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
from app.api.v1.deps import get_charger_service, get_current_user
from app.main import app
from app.services.charger_service import ChargerService
from app.models.enums import UserRole

class TestCharger(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=ChargerService)
        
        # Override dependency
        app.dependency_overrides[get_charger_service] = lambda: self.mock_service
        
        # Default user mock (Owner)
        self.mock_user = MagicMock()
        self.mock_user.id = 10
        self.mock_user.role = UserRole.owner
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_chargers(self):
        m = MagicMock(
            id=1, owner_id=1, 
            latitude=50.0, longitude=14.0,
            street="S", house_number="1", city="C", postal_code="123", region="R",
            ocpp_id="V-001",
            vendor=None, model=None, serial_number=None, firmware_version=None,
            is_active=True, is_enabled=True, created_at="2023-01-01T00:00:00"
        )
        m.name = "C1"
        self.mock_service.list_chargers.return_value = [m]
        
        response = self.client.get("/api/v1/chargers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create_charger_as_owner(self):
        m = MagicMock(
            id=1, owner_id=1, 
            latitude=50.0, longitude=14.0,
            street=None, house_number=None, city=None, postal_code=None, region=None,
            ocpp_id="V-001",
            vendor=None, model=None, serial_number=None, firmware_version=None,
            is_active=True, is_enabled=True, created_at="2023-01-01T00:00:00"
        )
        m.name = "New Charger"
        self.mock_service.create_charger.return_value = m
        
        response = self.client.post("/api/v1/chargers/", json={
            "name": "New Charger",
            "latitude": 50.0,
            "longitude": 14.0
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "New Charger")
        
    def test_create_charger_forbidden_for_user(self):
        # Demote to User
        self.mock_user.role = UserRole.user
        
        response = self.client.post("/api/v1/chargers/", json={
             "name": "New Charger",
             "latitude": 50.0,
             "longitude": 14.0
        })
        self.assertEqual(response.status_code, 403)

    def test_get_charger_detail(self):        # Mock
        m = MagicMock(
            id=1, owner_id=1, 
            latitude=50.0, longitude=14.0, ocpp_id="V-001",
            street=None, house_number=None, city=None, postal_code=None, region=None,
            vendor=None, model=None, serial_number=None, firmware_version=None,
            is_active=True, is_enabled=True, created_at="2023-01-01T00:00:00"
        )
        m.name = "C1"
        self.mock_service.get_charger.return_value = m
        response = self.client.get("/api/v1/chargers/1")
        self.assertEqual(response.status_code, 200)
        
    def test_update_charger_success(self):
        # Mock existing charger owned by user
        mock_charger = MagicMock()
        mock_charger.id = 1
        mock_charger.owner_id = 10 # Same as current_user
        self.mock_service.get_charger.return_value = mock_charger
        
        m = MagicMock(
            id=1, 
            owner_id=10,
            latitude=50.0,
            longitude=14.0,
            street=None, house_number=None, city=None, postal_code=None, region=None,
            ocpp_id="V-001",
            vendor=None, model=None, serial_number=None, firmware_version=None,
            is_active=True, is_enabled=True, created_at="2023-01-01T00:00:00"
        )
        m.name = "Updated Name"
        self.mock_service.update_charger.return_value = m
        
        response = self.client.patch("/api/v1/chargers/1", json={"name": "Updated Name"})
        self.assertEqual(response.status_code, 200)
        
    def test_update_charger_failure_not_owner(self):
        # Mock existing charger owned by someone else
        mock_charger = MagicMock()
        mock_charger.id = 1
        mock_charger.owner_id = 999 
        self.mock_service.get_charger.return_value = mock_charger
        
        response = self.client.patch("/api/v1/chargers/1", json={"name": "Updated Name"})
        self.assertEqual(response.status_code, 403)

    def test_delete_charger_success(self):
        mock_charger = MagicMock()
        mock_charger.id = 1
        mock_charger.owner_id = 10
        self.mock_service.get_charger.return_value = mock_charger
        
        response = self.client.delete("/api/v1/chargers/1")
        self.assertEqual(response.status_code, 204)

if __name__ == "__main__":
    unittest.main()
