import unittest
from unittest.mock import AsyncMock, MagicMock
from app.services.rfid_service import RFIDService
from app.models.rfid import RFIDCardUpdate
from app.db.schema import RFIDCard

class TestRFIDSync(unittest.IsolatedAsyncioTestCase):
    async def test_rfid_delete_sets_enabled_false(self):
        # Setup
        mock_session = AsyncMock()
        service = RFIDService(mock_session)
        
        mock_card = RFIDCard(id=1, is_active=True, is_enabled=True)
        
        # Mock get_card
        service.get_card = AsyncMock(return_value=mock_card)
        
        # Execute delete
        await service.delete_card(1)
        
        # Verify
        self.assertFalse(mock_card.is_active)
        self.assertFalse(mock_card.is_enabled)
        mock_session.commit.assert_awaited_once()

    async def test_rfid_update_auto_disable_when_deactivating(self):
        # Setup
        mock_session = AsyncMock()
        service = RFIDService(mock_session)
        
        mock_card = RFIDCard(id=1, is_active=True, is_enabled=True)
        service.get_card = AsyncMock(return_value=mock_card)
        service.get_card_by_uid = AsyncMock(return_value=None) 
        
        # Update: Set is_active=False
        data = RFIDCardUpdate(is_active=False)
        
        await service.update_card(1, data)
        
        # Verify: is_enabled should be forced to False
        self.assertFalse(mock_card.is_active)
        self.assertFalse(mock_card.is_enabled)

    async def test_rfid_update_validation_error_enable_inactive(self):
        # Setup
        mock_session = AsyncMock()
        service = RFIDService(mock_session)
        
        # Card is inactive and disabled
        mock_card = RFIDCard(id=1, is_active=False, is_enabled=False)
        service.get_card = AsyncMock(return_value=mock_card)
        
        # Update: Try to set is_enabled=True WITHOUT setting is_active=True
        data = RFIDCardUpdate(is_enabled=True)
        
        # Verify: Should raise ValueError
        with self.assertRaises(ValueError):
            await service.update_card(1, data)

    async def test_rfid_update_allow_enable_if_activating(self):
        # Setup
        mock_session = AsyncMock()
        service = RFIDService(mock_session)
        
        # Card is inactive and disabled
        mock_card = RFIDCard(id=1, is_active=False, is_enabled=False)
        service.get_card = AsyncMock(return_value=mock_card)
        service.get_card_by_uid = AsyncMock(return_value=None)
        
        # Update: Set both is_enabled=True AND is_active=True
        data = RFIDCardUpdate(is_enabled=True, is_active=True)
        
        await service.update_card(1, data)
        
        # Verify: Should succeed
        self.assertTrue(mock_card.is_active)
        self.assertTrue(mock_card.is_enabled)
