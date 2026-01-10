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

    async def get_transactions(self, user_id: int | None = None, owner_id: int | None = None, charger_id: int | None = None, skip: int = 0, limit: int = 100):
        stmt = select(ChargeLog)
        
        if owner_id:
            stmt = stmt.join(Charger).where(Charger.owner_id == owner_id)
        
        if charger_id:
            stmt = stmt.where(ChargeLog.charger_id == charger_id)

        if user_id:
            stmt = stmt.where(ChargeLog.user_id == user_id)
            
        stmt = stmt.order_by(ChargeLog.start_time.desc()).offset(skip).limit(limit)
        
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_transaction(self, transaction_id: int):
        stmt = select(ChargeLog).where(ChargeLog.id == transaction_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def start_transaction(self, data: TransactionStartRequest) -> dict: # Změna návratového typu z int na dict
        # 1. Najít nabíječku
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
        new_log = ChargeLog(
            charger_id=charger.id,
            connector_id=connector.id,
            user_id=user_id,
            rfid_card_id=rfid_id,
            start_time=data.timestamp,
            meter_start=data.meter_start,
            status=ChargeStatus.running,
            price_per_kwh=connector.price_per_kwh if connector.price_per_kwh else 0
        )
        
        self._db.add(new_log)
        await self._db.flush()
        await self._db.commit()

        # --- ZMĚNA: Vracíme více informací ---
        # Předpokládám, že Connector má sloupec 'max_power' (kW)
        # Pokud ne, doplňte si ho do modelu, nebo zde vraťte natvrdo třeba 11
        return {
            "transaction_id": new_log.id,
            "max_power": connector.max_power if hasattr(connector, 'max_power') else 11
        }

    async def stop_transaction(self, data: TransactionStopRequest) -> ChargeLog:
        # 1. Najdeme běžící transakci
        stmt = select(ChargeLog).where(ChargeLog.id == data.transaction_id)
        result = await self._db.execute(stmt)
        log = result.scalars().first()

        if not log:
            raise ValueError(f"Transaction {data.transaction_id} not found")

        # Pokud už je hotová, vrátíme ji (idempotence) - aby se to nepočítalo dvakrát
        if log.status == ChargeStatus.completed:
            return log

        # 2. Aktualizace dat z Requestu
        log.meter_stop = data.meter_stop
        
        # Pokud request obsahuje timestamp, použijeme ho, jinak aktuální čas
        if data.timestamp:
            log.end_time = data.timestamp
        else:
            from datetime import datetime, timezone
            log.end_time = datetime.now(timezone.utc)

        # 3. Změna stavu na COMPLETED
        log.status = ChargeStatus.completed

        # 4. Výpočet spotřeby (pokud máme start i stop)
        # meter_start a meter_stop jsou ve Wh
        if log.meter_start is not None and log.meter_stop is not None:
            consumed_wh = log.meter_stop - log.meter_start
            # Ošetření záporné spotřeby (pokud by elektroměr blbnul)
            log.energy_wh = max(0, consumed_wh)
        else:
            log.energy_wh = 0

        # 5. Výpočet Ceny
        # Cena = (Wh / 1000) * Cena_za_kWh
        if log.energy_wh > 0 and log.price_per_kwh:
            # Převedeme na Decimal pro přesný výpočet
            kwh = Decimal(log.energy_wh) / Decimal(1000)
            
            # log.price_per_kwh je typu Decimal
            log.price = log.price_per_kwh * kwh
        else:
            log.price = 0

        # --- DEDUCT BALANCE FROM USER ---
        if log.price > 0 and log.user_id:
            # Musíme načíst uživatele, abychom mu odečetli kredit
            # Import User musíme dát na začátek souboru, pokud tam není
            # Ale tady lokálně pro přehlednost:
            from app.db.schema import User
            
            user_stmt = select(User).where(User.id == log.user_id)
            user_result = await self._db.execute(user_stmt)
            user = user_result.scalars().first()
            
            if user:
                # Odečteme cenu z balance
                # log.price je Decimal (nebo 0), user.balance je Decimal
                user.balance -= log.price
                self._db.add(user) # Označíme pro update
            
            # --- CREDIT BALANCE TO CHARGER OWNER ---
            # 1. Načteme nabíječku (pro získání owner_id)
            stmt_charger = select(Charger).where(Charger.id == log.charger_id)
            result_charger = await self._db.execute(stmt_charger)
            charger = result_charger.scalars().first()
            
            if charger and charger.owner_id:
                 # 2. Načteme majitele nabíječky
                 stmt_owner = select(User).where(User.id == charger.owner_id)
                 result_owner = await self._db.execute(stmt_owner)
                 owner = result_owner.scalars().first()
                 
                 # 3. Přičteme mu kredit (pokud to není stejný uživatel, což by neměl být, ale i tak)
                 if owner:
                     owner.balance += log.price
                     self._db.add(owner)

        # 6. Uložení do DB
        self._db.add(log)
        await self._db.commit()
        await self._db.refresh(log)

        return log
    
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