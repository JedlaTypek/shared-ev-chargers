from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.db.schema import ChargeLog, Charger, Connector, RFIDCard
from app.models.charge_log import TransactionStartRequest, TransactionStopRequest
from app.models.enums import ChargeStatus

class TransactionService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def start_transaction(self, data: TransactionStartRequest) -> int:
        # 1. Najít nabíječku podle OCPP ID
        stmt = select(Charger).where(Charger.ocpp_id == data.ocpp_id)
        result = await self._db.execute(stmt)
        charger = result.scalars().first()
        if not charger:
            raise HTTPException(status_code=404, detail="Charger not found")

        # 2. Najít konektor
        stmt_conn = select(Connector).where(
            Connector.charger_id == charger.id,
            Connector.ocpp_number == data.connector_id
        )
        result_conn = await self._db.execute(stmt_conn)
        connector = result_conn.scalars().first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")

        # 3. Najít uživatele/kartu
        stmt_rfid = select(RFIDCard).where(RFIDCard.card_uid == data.id_tag)
        result_rfid = await self._db.execute(stmt_rfid)
        rfid_card = result_rfid.scalars().first()
        
        user_id = rfid_card.owner_id if rfid_card else None
        rfid_id = rfid_card.id if rfid_card else None

        # 4. Vytvořit záznam
        # Pozor: Nepředáváme transaction_id, protože v DB tabulce tento sloupec není.
        # Jako TransactionID pro OCPP použijeme primární klíč (id) tohoto řádku.
        new_log = ChargeLog(
            charger_id=charger.id,
            connector_id=connector.id,
            user_id=user_id,
            rfid_card_id=rfid_id,
            start_time=data.timestamp,
            meter_start=data.meter_start,
            status=ChargeStatus.running, # Opraveno na malé písmena podle Enumu
            price_per_kwh=connector.price_per_kwh if connector.price_per_kwh else 0
        )
        
        self._db.add(new_log)
        await self._db.flush() # Tímto se vygeneruje new_log.id
        await self._db.commit()

        # Vracíme ID řádku jako TransactionID
        return new_log.id

    async def stop_transaction(self, data: TransactionStopRequest):
        # 1. Najít transakci podle ID
        stmt = select(ChargeLog).where(ChargeLog.id == data.transaction_id)
        result = await self._db.execute(stmt)
        log = result.scalars().first()

        if not log:
            # Pokud transakce neexistuje, vrátíme úspěch, aby se nabíječka nezasekla
            # (Může se stát, pokud server spadl a ztratil data z paměti, ale v DB by to být mělo)
            return {"status": "Ignored"}

        # 2. Výpočty
        meter_stop = data.meter_stop
        consumed_wh = max(0, meter_stop - log.meter_start)
        consumed_kwh = Decimal(consumed_wh) / Decimal(1000)
        
        price = consumed_kwh * log.price_per_kwh

        # 3. Update záznamu
        log.meter_stop = meter_stop
        log.end_time = data.timestamp
        log.energy_wh = consumed_wh
        log.price = round(price, 2)
        log.status = ChargeStatus.completed # Opraveno na malé písmena podle Enumu

        await self._db.commit()
        return {"status": "Accepted"}