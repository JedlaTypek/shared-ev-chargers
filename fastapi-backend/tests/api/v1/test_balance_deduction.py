import unittest
from unittest.mock import AsyncMock, MagicMock, call
from decimal import Decimal
from datetime import datetime
from app.services.transaction_service import TransactionService
from app.models.charge_log import TransactionStopRequest
from app.models.enums import ChargeStatus
from app.db.schema import ChargeLog, User, Charger

class TestBalanceDeduction(unittest.IsolatedAsyncioTestCase):
    async def test_balance_deduction_success(self):
        # Setup
        mock_session = AsyncMock()
        service = TransactionService(mock_session)
        
        # Data
        user_id = 123
        initial_balance = Decimal("100.00")
        price_per_kwh = Decimal("10.00")
        conn_max_power_w = 22000
        
        mock_user = User(id=user_id, balance=initial_balance)
        mock_log = ChargeLog(
            id=1, 
            user_id=user_id, 
            status=ChargeStatus.running,
            meter_start=0,
            price_per_kwh=price_per_kwh
        )
        
        # Mocks for DB calls
        # We expect 2 queries: one for transaction, one for user
        # 1. select(ChargeLog)
        mock_result_log = MagicMock()
        mock_result_log.scalars.return_value.first.return_value = mock_log
        
        # 2. select(User)
        mock_result_user = MagicMock()
        mock_result_user.scalars.return_value.first.return_value = mock_user

        # 3. select(Charger) - NEW: Return None to skip owner credit logic in this test
        mock_result_charger = MagicMock()
        mock_result_charger.scalars.return_value.first.return_value = None
        
        # Prepare side_effect for session.execute
        # Note: In the actual code, execute is awaited.
        mock_session.execute.side_effect = [mock_result_log, mock_result_user, mock_result_charger]
        
        # Input Data
        stop_req = TransactionStopRequest(
            transaction_id=1,
            meter_stop=5000, # 5 kWh
            timestamp=datetime.now()
        )
        
        # Execute
        result_log = await service.stop_transaction(stop_req)
        
        # Verify
        # Energy: 5000 Wh = 5 kWh
        # Price: 5 * 10.00 = 50.00
        self.assertEqual(result_log.energy_wh, 5000)
        self.assertEqual(result_log.price, Decimal("50.00"))
        
        # User Balance: 100.00 - 50.00 = 50.00
        self.assertEqual(mock_user.balance, Decimal("50.00"))
        
        # Check commits
        self.assertTrue(mock_session.commit.called)
        
    async def test_balance_deduction_zero_price(self):
        # Setup
        mock_session = AsyncMock()
        service = TransactionService(mock_session)
        
        user_id = 123
        initial_balance = Decimal("100.00")
        
        mock_user = User(id=user_id, balance=initial_balance)
        mock_log = ChargeLog(
            id=1, 
            user_id=user_id, 
            status=ChargeStatus.running,
            meter_start=0,
            price_per_kwh=Decimal("0.00") # Free charging
        )
        
        # 1. select(ChargeLog)
        mock_result_log = MagicMock()
        mock_result_log.scalars.return_value.first.return_value = mock_log
        
        # No User query expected if price is 0
        mock_session.execute.side_effect = [mock_result_log]
        
        stop_req = TransactionStopRequest(
            transaction_id=1,
            meter_stop=5000,
            timestamp=datetime.now()
        )
        
        await service.stop_transaction(stop_req)
        
        self.assertEqual(mock_log.price, 0)
        self.assertEqual(mock_user.balance, initial_balance) # Unchanged

    async def test_balance_goes_negative(self):
        # Setup
        mock_session = AsyncMock()
        service = TransactionService(mock_session)
        
        # Data: User has 10.00, Charge costs 50.00
        user_id = 123
        initial_balance = Decimal("10.00")
        price_per_kwh = Decimal("10.00") 
        
        mock_user = User(id=user_id, balance=initial_balance)
        mock_log = ChargeLog(
            id=1, 
            user_id=user_id, 
            status=ChargeStatus.running,
            meter_start=0,
            price_per_kwh=price_per_kwh
        )
        
        mock_result_log = MagicMock()
        mock_result_log.scalars.return_value.first.return_value = mock_log
        mock_result_user = MagicMock()
        mock_result_user.scalars.return_value.first.return_value = mock_user
        
        # 3. select(Charger) - Skip owner logic
        mock_result_charger = MagicMock()
        mock_result_charger.scalars.return_value.first.return_value = None

        mock_session.execute.side_effect = [mock_result_log, mock_result_user, mock_result_charger]
        
        stop_req = TransactionStopRequest(
            transaction_id=1,
            meter_stop=5000, # 5 kWh * 10 = 50.00 cost
            timestamp=datetime.now()
        )
        
        await service.stop_transaction(stop_req)
        
        # Verify
        # 10.00 - 50.00 = -40.00
        self.assertEqual(mock_user.balance, Decimal("-40.00"))

    async def test_balance_transfer_user_to_owner(self):
        # Setup
        mock_session = AsyncMock()
        service = TransactionService(mock_session)
        
        # User (Payer)
        user_id = 100
        user_balance_start = Decimal("100.00")
        mock_user = User(id=user_id, balance=user_balance_start)

        # Owner (Receiver)
        owner_id = 999
        owner_balance_start = Decimal("50.00")
        mock_owner = User(id=owner_id, balance=owner_balance_start)
        
        # Charger
        mock_charger = Charger(id=55, owner_id=owner_id)

        # Log
        price_per_kwh = Decimal("10.00")
        mock_log = ChargeLog(
            id=1, 
            user_id=user_id, 
            charger_id=55,
            status=ChargeStatus.running,
            meter_start=0,
            price_per_kwh=price_per_kwh
        )
        
        # Mock DB chaining
        mock_result_log = MagicMock()
        mock_result_log.scalars.return_value.first.return_value = mock_log
        
        mock_result_user = MagicMock()
        mock_result_user.scalars.return_value.first.return_value = mock_user

        mock_result_charger = MagicMock()
        mock_result_charger.scalars.return_value.first.return_value = mock_charger

        mock_result_owner = MagicMock()
        mock_result_owner.scalars.return_value.first.return_value = mock_owner
        
        # Sequentital calls:
        # 1. select(ChargeLog) -> transaction
        # 2. select(User) -> payer (deduct)
        # 3. select(Charger) -> get owner_id
        # 4. select(User) -> owner (credit)
        mock_session.execute.side_effect = [
            mock_result_log, 
            mock_result_user, 
            mock_result_charger, 
            mock_result_owner
        ]
        
        stop_req = TransactionStopRequest(
            transaction_id=1,
            meter_stop=1000, # 1 kWh => 10.00 cost
            timestamp=datetime.now()
        )
        
        await service.stop_transaction(stop_req)
        
        # Verify Payer (Deduction)
        # 100 - 10 = 90
        self.assertEqual(mock_user.balance, Decimal("90.00"))

        # Verify Owner (Credit)
        # 50 + 10 = 60
        self.assertEqual(mock_owner.balance, Decimal("60.00"))
