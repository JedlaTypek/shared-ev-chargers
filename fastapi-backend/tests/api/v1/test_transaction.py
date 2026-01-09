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
from app.api.v1.deps import get_transaction_service, get_current_user
from app.main import app
from app.services.transaction_service import TransactionService
from app.models.enums import UserRole, ChargeStatus

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=TransactionService)
        
        # Override dependency
        app.dependency_overrides[get_transaction_service] = lambda: self.mock_service
        
        # Default user mock (User)
        self.mock_user = MagicMock()
        self.mock_user.id = 1
        self.mock_user.role = UserRole.user
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_transactions(self):
        mock_tx = MagicMock()
        mock_tx.id = 1
        mock_tx.status = ChargeStatus.completed
        mock_tx.energy_wh = 100
        mock_tx.price = 10.0
        mock_tx.user_id = 1
        mock_tx.start_time = "2023-01-01T10:00:00"
        
        self.mock_service.get_transactions.return_value = [mock_tx]
        
        response = self.client.get("/api/v1/transactions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        # Should verify service was called with user_id=1
        self.mock_service.get_transactions.assert_called_with(
            user_id=1, charger_id=None, skip=0, limit=50
        )

    def test_list_transactions_as_admin(self):
        self.mock_user.role = UserRole.admin
        
        self.mock_service.get_transactions.return_value = []
        
        response = self.client.get("/api/v1/transactions/")
        self.assertEqual(response.status_code, 200)
        # Admin calls without user_id filter
        self.mock_service.get_transactions.assert_called_with(
            skip=0, limit=50, charger_id=None
        )

    def test_get_transaction_detail(self):
        mock_tx = MagicMock()
        mock_tx.id = 1
        mock_tx.user_id = 1
        mock_tx.status = ChargeStatus.completed
        mock_tx.start_time = "2023-01-01T10:00:00"
        mock_tx.price = 10.0
        mock_tx.energy_wh = 100
        
        self.mock_service.get_transaction.return_value = mock_tx
        
        response = self.client.get("/api/v1/transactions/1")
        self.assertEqual(response.status_code, 200)

    def test_get_transaction_forbidden(self):
        mock_tx = MagicMock()
        mock_tx.id = 1
        mock_tx.user_id = 999 # Not me
        mock_tx.status = ChargeStatus.completed
        mock_tx.start_time = "2023-01-01T10:00:00"
        mock_tx.price = 10.0
        mock_tx.energy_wh = 100
        
        self.mock_service.get_transaction.return_value = mock_tx
        
        response = self.client.get("/api/v1/transactions/1")
        self.assertEqual(response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
