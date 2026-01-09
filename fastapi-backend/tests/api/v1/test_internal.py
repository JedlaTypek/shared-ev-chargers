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
os.environ.setdefault("API_KEY", "test_api_key") # Set specific key
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("DEBUG", "True")

from fastapi.testclient import TestClient
from app.api.v1.deps import get_charger_service, get_connector_service, get_transaction_service
from app.main import app
from app.services.charger_service import ChargerService
from app.services.connector_service import ConnectorService
from app.services.transaction_service import TransactionService
from app.models.charger import ChargerTechnicalStatus

class TestInternal(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        self.mock_charger_service = AsyncMock(spec=ChargerService)
        self.mock_connector_service = AsyncMock(spec=ConnectorService)
        self.mock_transaction_service = AsyncMock(spec=TransactionService)
        
        # Override dependencies
        app.dependency_overrides[get_charger_service] = lambda: self.mock_charger_service
        app.dependency_overrides[get_connector_service] = lambda: self.mock_connector_service
        app.dependency_overrides[get_transaction_service] = lambda: self.mock_transaction_service
        
        self.headers = {"x-api-key": "test_api_key"}
        
        # Patch config to ensure api_key matches even if loaded earlier
        self.config_patcher = patch("app.core.config.config.api_key", "test_api_key")
        self.config_patcher.start()

    def tearDown(self):
        app.dependency_overrides = {}
        self.config_patcher.stop()

    def test_heartbeat(self):
        response = self.client.post("/api/v1/internal/heartbeat/CP1", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("currentTime", response.json())
        self.mock_charger_service.update_heartbeat.assert_called_with("CP1")

    def test_boot_notification(self):
        self.mock_charger_service.update_technical_status.return_value = {
            "id": 1,
            "ocpp_id": "CP1",
            "owner_id": 1,
            "created_at": "2023-01-01T00:00:00",
            "name": "Charger",
            "latitude": 50.0,
            "longitude": 14.0
        }
        
        data = {
            "vendor": "TestVendor",
            "model": "TestModel"
        }
        
        response = self.client.post("/api/v1/internal/boot-notification/CP1", json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_authorize(self):
        self.mock_charger_service.authorize_tag.return_value = {"status": "Accepted"}
        
        response = self.client.post("/api/v1/internal/authorize/CP1", json={"id_tag": "AABBCC"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["idTagInfo"]["status"], "Accepted")

    def test_check_charger_exists(self):
        self.mock_charger_service.check_exists_by_ocpp.return_value = {
            "id": 1, "is_active": True
        }
        
        response = self.client.get("/api/v1/internal/charger/exists/CP1", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_check_charger_exists_inactive(self):
        self.mock_charger_service.check_exists_by_ocpp.return_value = {
            "id": 1, "is_active": False
        }
        
        response = self.client.get("/api/v1/internal/charger/exists/CP1", headers=self.headers)
        self.assertEqual(response.status_code, 403)

    def test_connector_status(self):
        mock_conn = MagicMock()
        mock_conn.id = 1
        self.mock_connector_service.process_status_notification.return_value = mock_conn
        
        data = {
            "ocpp_id": "CP1",
            "connector_number": 1,
            "status": "Available"
        }
        
        response = self.client.post("/api/v1/internal/connector-status", json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_start_transaction(self):
        self.mock_transaction_service.start_transaction.return_value = {
            "transaction_id": 100,
            "max_power": 11.0
        }
        
        data = {
            "ocpp_id": "CP1",
            "connector_id": 1,
            "id_tag": "AABBCC",
            "meter_start": 0,
            "timestamp": "2023-01-01T10:00:00"
        }
        
        response = self.client.post("/api/v1/internal/transaction/start", json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["transactionId"], 100)

    def test_api_key_invalid(self):
        response = self.client.post("/api/v1/internal/heartbeat/CP1", headers={"x-api-key": "wrong"})
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
