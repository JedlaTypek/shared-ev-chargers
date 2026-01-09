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

from app.models.user import UserUpdate, UserCreate
from app.db.schema import User
from app.services.user_service import UserService

class TestUserServicePasswordChange(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.mock_db = AsyncMock()
        self.service = UserService(self.mock_db)
        
        # Setup a dummy user
        self.user_password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.0xJ0k1j0j0j0j0j0j0j0j0j" # Mock hash
        self.user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            password=self.user_password_hash,
            role="user",
            balance=Decimal("100.00"),
            is_active=True
        )
        
        # Mock get_user to return our user
        self.service.get_user = AsyncMock(return_value=self.user)
        
    @patch("app.services.user_service.verify_password")
    @patch("app.services.user_service.get_password_hash")
    async def test_update_password_success(self, mock_hash, mock_verify):
        """Test successful password update with correct old password"""
        mock_verify.return_value = True # Old password is correct
        mock_hash.return_value = "new_hashed_password"
        
        user_update = UserUpdate(password="new_secret", old_password="old_secret")
        
        updated_user = await self.service.update_user(1, user_update, verify_old_password=True)
        
        self.assertIsNotNone(updated_user)
        mock_verify.assert_called_with("old_secret", self.user_password_hash)
        mock_hash.assert_called_with("new_secret")
        self.assertEqual(updated_user.password, "new_hashed_password") # Should be updated on object
        
    @patch("app.services.user_service.verify_password")
    async def test_update_password_wrong_old_password(self, mock_verify):
        """Test password update with incorrect old password"""
        mock_verify.return_value = False # Old password is WRONG
        
        user_update = UserUpdate(password="new_secret", old_password="wrong_secret")
        
        with self.assertRaises(ValueError) as cm:
            await self.service.update_user(1, user_update, verify_old_password=True)
            
        self.assertEqual(str(cm.exception), "Incorrect old password")
        
    async def test_update_password_missing_old_password(self):
        """Test password update without providing old password"""
        user_update = UserUpdate(password="new_secret") # No old_password
        
        with self.assertRaises(ValueError) as cm:
            await self.service.update_user(1, user_update, verify_old_password=True)
            
        self.assertEqual(str(cm.exception), "Old password is required to change password")

    @patch("app.services.user_service.get_password_hash")
    async def test_admin_change_user_password(self, mock_hash):
        """Test Admin changing user password (no old password required)"""
        mock_hash.return_value = "admin_set_hash"
        
        # Admin doesn't need to know old password
        user_update = UserUpdate(password="new_secret_by_admin") 
        
        updated_user = await self.service.update_user(1, user_update, verify_old_password=False)
        
        self.assertIsNotNone(updated_user)
        mock_hash.assert_called_with("new_secret_by_admin")
        self.assertEqual(updated_user.password, "admin_set_hash")
        
    async def test_update_other_fields_no_password(self):
        """Test updating other fields without password change"""
        user_update = UserUpdate(name="New Name")
        
        updated_user = await self.service.update_user(1, user_update, verify_old_password=True)
        
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, "New Name")
        # Password should remain unchanged
        self.assertEqual(updated_user.password, self.user_password_hash)

if __name__ == "__main__":
    unittest.main()
