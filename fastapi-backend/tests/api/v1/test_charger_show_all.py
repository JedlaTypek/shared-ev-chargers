import os
import unittest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Set env vars
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("DEBUG", "True")

from app.api.v1.deps import get_charger_service, get_current_user, get_current_user_optional
from app.main import app
from app.services.charger_service import ChargerService
from app.models.enums import UserRole
from app.db.schema import User

class TestChargerShowAll(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_service = AsyncMock(spec=ChargerService)
        app.dependency_overrides[get_charger_service] = lambda: self.mock_service
        # Reset other overrides
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_current_user_optional in app.dependency_overrides:
            del app.dependency_overrides[get_current_user_optional]

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_chargers_show_all_admin(self):
        # 1. Admin + show_all=True -> sees all
        m_active = MagicMock(id=1, is_active=True, is_enabled=True, vendor=None, model=None, serial_number=None, firmware_version=None, street=None, house_number=None, city=None, postal_code=None, region=None)
        m_active.name = "Active"
        m_active.ocpp_id = "V-001"
        
        m_deleted = MagicMock(id=2, is_active=False, is_enabled=True, vendor=None, model=None, serial_number=None, firmware_version=None, street=None, house_number=None, city=None, postal_code=None, region=None)
        m_deleted.name = "Deleted"
        m_deleted.ocpp_id = "V-002"
        
        # Admin mocks
        admin_user = MagicMock(spec=User)
        admin_user.id = 10
        admin_user.role = UserRole.admin
        
        # Important: get_current_user_optional is used in list_chargers
        app.dependency_overrides[get_current_user_optional] = lambda: admin_user
        
        self.mock_service.list_chargers.return_value = [m_active, m_deleted]
        
        response = self.client.get("/api/v1/chargers/?show_all=true")
        self.assertEqual(response.status_code, 200)
        # Verify service was called with show_all=True
        self.mock_service.list_chargers.assert_called_with(show_all=True)

    def test_list_chargers_mine_show_all(self):
        # 1. Owner + mine=True + show_all=True -> sees own deleted
        m_deleted = MagicMock(id=1, owner_id=1, is_active=False, vendor=None, model=None, serial_number=None, firmware_version=None, street=None, house_number=None, city=None, postal_code=None, region=None)
        m_deleted.name = "My Deleted"
        m_deleted.ocpp_id = "V-003"
        self.mock_service.list_chargers.return_value = [m_deleted]
        
        user = MagicMock(spec=User)
        user.id = 1
        user.role = UserRole.user
        
        app.dependency_overrides[get_current_user_optional] = lambda: user
        
        response = self.client.get("/api/v1/chargers/?mine=true&show_all=true")
        self.assertEqual(response.status_code, 200)
        self.mock_service.list_chargers.assert_called_with(owner_id=1, show_all=True)

    def test_list_chargers_public_ignores_show_all(self):
        # Public user (or unauth) tries show_all=true -> ignored (show_all=False)
        m_active = MagicMock(id=1, is_active=True, vendor=None, model=None, serial_number=None, firmware_version=None, street=None, house_number=None, city=None, postal_code=None, region=None)
        m_active.name = "Active"
        m_active.ocpp_id = "V-004"
        self.mock_service.list_chargers.return_value = [m_active]
        
        # No user logged in
        app.dependency_overrides[get_current_user_optional] = lambda: None
        
        response = self.client.get("/api/v1/chargers/?show_all=true")
        self.assertEqual(response.status_code, 200)
        # Verify service called with show_all=False (default or explicit False)
        # Because effective_show_all = show_all (True) and is_admin (False) -> False
        self.mock_service.list_chargers.assert_called_with(show_all=False)

if __name__ == "__main__":
    unittest.main()
