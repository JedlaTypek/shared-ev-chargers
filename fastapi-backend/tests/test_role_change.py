import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

# Add app to path
sys.path.append("/home/jedla/projects/shared-ev-chargers/fastapi-backend")

import os
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("DEBUG", "True")

from app.models.user import UserUpdate
from app.api.v1.user import update_user
from app.models.enums import UserRole
from app.db.schema import User
from fastapi import HTTPException

class TestRoleChange(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.mock_service = AsyncMock()
        
        # Setup dummy user
        self.user_data_owner = UserUpdate(role=UserRole.owner)
        self.user_data_user = UserUpdate(role=UserRole.user)
        self.user_data_admin = UserUpdate(role=UserRole.admin)
        
        self.current_user = User(
            id=1,
            role=UserRole.user,
            password="hash",
            email="test@test.com"
        )
        
        self.admin_user = User(
            id=99,
            role=UserRole.admin,
            password="hash",
            email="admin@test.com"
        )

    async def test_user_can_switch_to_owner(self):
        """Test User -> Owner switch"""
        # User updating self
        self.mock_service.update_user.return_value = User(id=1, role=UserRole.owner)
        
        result = await update_user(1, self.user_data_owner, self.mock_service, self.current_user)
        self.assertEqual(result.role, UserRole.owner)
        
    async def test_owner_can_switch_to_user(self):
        """Test Owner -> User switch"""
        self.current_user.role = UserRole.owner
        self.mock_service.update_user.return_value = User(id=1, role=UserRole.user)
        
        result = await update_user(1, self.user_data_user, self.mock_service, self.current_user)
        self.assertEqual(result.role, UserRole.user)
        
    async def test_user_cannot_switch_to_admin(self):
        """Test User -> Admin switch forbidden"""
        with self.assertRaises(HTTPException) as cm:
             await update_user(1, self.user_data_admin, self.mock_service, self.current_user)
             
        self.assertEqual(cm.exception.status_code, 403)
        self.assertEqual(cm.exception.detail, "Cannot set role to admin")

    async def test_admin_can_promote_user(self):
        """Test Admin can make User into Admin"""
        # Admin updating user 1
        self.mock_service.update_user.return_value = User(id=1, role=UserRole.admin)
        
        result = await update_user(1, self.user_data_admin, self.mock_service, self.admin_user)
        self.assertEqual(result.role, UserRole.admin)

if __name__ == "__main__":
    unittest.main()
