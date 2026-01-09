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
from app.api.v1.deps import get_connector_service, get_current_user
from app.main import app
from app.services.connector_service import ConnectorService
from app.models.enums import UserRole, ConnectorType, CurrentType

class TestConnector(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=ConnectorService)
        
        # Override dependency
        app.dependency_overrides[get_connector_service] = lambda: self.mock_service
        
        # Default user mock (Owner)
        self.mock_user = MagicMock()
        self.mock_user.id = 10
        self.mock_user.role = UserRole.owner
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_get_connector_detail(self):
        # returns ConnectorRead compatible dict/object
        self.mock_service.get_connector_with_status.return_value = {
            "id": 1, 
            "charger_id": 1,
            "ocpp_number": 1,
            "type": ConnectorType.Type2,
            "current_type": CurrentType.AC,
            "max_power_w": 11000,
            "price_per_kwh": 5.50,
            "is_active": True,
            "status": "Available"
        }
        
        response = self.client.get("/api/v1/connectors/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Available")

    def test_update_connector_success(self):
        # Mock connector ORM object with relationship to charger
        mock_connector = MagicMock()
        mock_connector.id = 1
        mock_connector.charger.owner_id = 10 # Same as user
        
        self.mock_service.get_connector.return_value = mock_connector
        
        # Result of update
        self.mock_service.get_connector_with_status.return_value = {
            "id": 1, 
            "charger_id": 1,
            "ocpp_number": 1,
            "max_power_w": 22000, # Updated
            "status": "Available"
        }
        
        response = self.client.patch("/api/v1/connectors/1", json={"max_power_w": 22000})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["max_power_w"], 22000)

    def test_update_connector_forbidden(self):
        # Mock connector owned by someone else
        mock_connector = MagicMock()
        mock_connector.id = 1
        mock_connector.charger.owner_id = 999 
        
        self.mock_service.get_connector.return_value = mock_connector
        
        response = self.client.patch("/api/v1/connectors/1", json={"max_power_w": 22000})
        self.assertEqual(response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
