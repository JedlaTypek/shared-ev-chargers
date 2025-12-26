from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.db.schema import ChargeLog, Charger, Connector, RFIDCard
from app.models.charge_log import TransactionMeterValueRequest, TransactionStartRequest, TransactionStopRequest
from app.models.enums import ChargeStatus

class TransactionService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def get_transactions(self, user_id: int | None = None, skip: int = 0, limit: int = 100):
        stmt = select(ChargeLog).order_by(ChargeLog.start_time.desc()).offset(skip).limit(limit)
        
        if user_id:
            stmt = stmt.where(ChargeLog.user_id == user_id)
            
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_transaction(self, transaction_id: int):
        stmt = select(ChargeLog).where(ChargeLog.id == transaction_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

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
    
    async def process_meter_value(self, data: TransactionMeterValueRequest):
        """
        Aktualizuje běžící transakci o aktuální stav elektroměru.
        """
        stmt = select(ChargeLog).where(ChargeLog.id == data.transaction_id)
        result = await self._db.execute(stmt)
        log = result.scalars().first()

        # Pokud transakce neexistuje nebo už není 'running', ignorujeme
        if not log or log.status != ChargeStatus.running:
            return

        # Aktualizujeme stav
        # Díky 'onupdate' v databázi se 'last_update' změní samo!
        log.meter_stop = data.meter_value
        
        # Přepočet energie
        consumed_wh = max(0, log.meter_stop - log.meter_start)
        log.energy_wh = consumed_wh

        # Volitelně: Průběžný výpočet ceny (pokud máš cenu v logu nebo na konektoru)
        if hasattr(log, 'price_per_kwh') and log.price_per_kwh:
             # pozor na převod typů (Decimal vs int)
             pass 

        await self._db.commit()

    async def close_stale_transactions(self, max_age_minutes: int = 15):
        """
        Najde transakce, které jsou 'running', ale o kterých jsme neslyšeli déle než X minut.
        """
        limit_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)

        stmt = select(ChargeLog).where(
            ChargeLog.status == ChargeStatus.running,
            ChargeLog.last_update < limit_time
        )
        result = await self._db.execute(stmt)
        stale_logs = result.scalars().all()

        count = 0
        for log in stale_logs:
            # Ukončíme jako Failed (nebo Completed, záleží na preferenci)
            log.status = ChargeStatus.failed 
            log.end_time = log.last_update # Ukončíme časem posledního kontaktu
            
            # Cena a energie už jsou tam uložené z posledního process_meter_value
            count += 1
        
        if count > 0:
            await self._db.commit()
        
        return count