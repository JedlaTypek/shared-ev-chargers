import os
import unittest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.api.v1.deps import get_transaction_service, get_current_user
from app.main import app
from app.services.transaction_service import TransactionService
from app.models.enums import UserRole

class TestTransactionFiltering(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=TransactionService)
        
        # Override dependency
        app.dependency_overrides[get_transaction_service] = lambda: self.mock_service
        
        # Default user mock (Owner)
        self.mock_user = MagicMock()
        self.mock_user.id = 10
        self.mock_user.role = UserRole.owner
        self.mock_user.is_active = True
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self):
        app.dependency_overrides = {}

    def test_get_transactions_as_owner_with_charger_filter(self):
        # Scenario: Owner requests logs for THEIR charger with ID 55
        self.mock_service.get_transactions.return_value = []
        
        response = self.client.get("/api/v1/transactions/?as_owner=true&charger_id=55")
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that Router calls Service with:
        # owner_id=10 (from current_user)
        # charger_id=55 (from query)
        self.mock_service.get_transactions.assert_called_with(
            owner_id=10, 
            charger_id=55, 
            skip=0, 
            limit=50
        )

    def test_get_transactions_as_owner_without_charger_filter(self):
        # Scenario: Owner requests all logs for THEIR chargers
        self.mock_service.get_transactions.return_value = []
        
        response = self.client.get("/api/v1/transactions/?as_owner=true")
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that Router calls Service with:
        # owner_id=10
        # charger_id=None
        self.mock_service.get_transactions.assert_called_with(
            owner_id=10, 
            charger_id=None, 
            skip=0, 
            limit=50
        )

    def test_get_transactions_as_user_ignoring_as_owner(self):
        # Scenario: Regular user tries to use as_owner=true (should be ignored or fall back to user logic)
        self.mock_user.role = UserRole.user # Downgrade to User
        self.mock_service.get_transactions.return_value = []
        
        response = self.client.get("/api/v1/transactions/?as_owner=true&charger_id=55")
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that Router calls Service with:
        # user_id=10 (me)
        # charger_id=55
        # as_owner flag logic not triggered for UserRole.user
        self.mock_service.get_transactions.assert_called_with(
            user_id=10, 
            charger_id=55, 
            skip=0, 
            limit=50
        )

if __name__ == "__main__":
    unittest.main()
