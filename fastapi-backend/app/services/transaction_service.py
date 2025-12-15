from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.db.schema import ChargeLog, Charger, Connector, RFIDCard, User
from app.models.charge_log import TransactionStartRequest, TransactionStopRequest
from app.models.enums import ChargeStatus

class TransactionService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def start_transaction(self, data: TransactionStartRequest) -> int:
        # 1. Najít nabíječku
        stmt = select(Charger).where(Charger.ocpp_id == data.ocpp_id)
        result = await self._db.execute(stmt)
        charger = result.scalars().first()
        if not charger:
            raise HTTPException(status_code=404, detail="Charger not found")

        # 2. Najít konektor (podle OCPP čísla na dané nabíječce)
        stmt_conn = select(Connector).where(
            Connector.charger_id == charger.id,
            Connector.ocpp_number == data.connector_id
        )
        result_conn = await self._db.execute(stmt_conn)
        connector = result_conn.scalars().first()
        if not connector:
            raise HTTPException(status_code=404, detail="Connector not found")

        # 3. Najít uživatele podle RFID
        stmt_rfid = select(RFIDCard).where(RFIDCard.card_uid == data.id_tag)
        result_rfid = await self._db.execute(stmt_rfid)
        rfid_card = result_rfid.scalars().first()
        
        user_id = rfid_card.owner_id if rfid_card else None
        # Pokud kartu neznáme, můžeme buď vyhodit chybu, nebo logovat jako "Anonym"
        # Zde předpokládáme, že Authorize proběhl a kartu známe.

        # 4. Vytvořit záznam
        new_log = ChargeLog(
            transaction_id=0, # Dočasně, po uložení se vygeneruje ID, které použijeme
            charger_id=charger.id,
            connector_id=connector.id,
            user_id=user_id,
            rfid_card_id=rfid_card.id if rfid_card else None,
            start_time=data.timestamp,
            meter_start=data.meter_start,
            status=ChargeStatus.RUNNING,
            # Uložíme si aktuální cenu konektoru, aby se neměnila zpětně
            price_per_kwh=connector.price_per_kwh 
        )
        
        self._db.add(new_log)
        await self._db.flush() # Získáme ID (primary key)
        
        # Některé systémy používají jako transactionId přímo ID řádku v DB
        new_log.transaction_id = new_log.id 
        await self._db.commit()

        return new_log.id

    async def stop_transaction(self, data: TransactionStopRequest):
        # 1. Najít transakci
        # Hledáme podle transaction_id (což je u nás ID řádku)
        stmt = select(ChargeLog).where(ChargeLog.id == data.transaction_id)
        result = await self._db.execute(stmt)
        log = result.scalars().first()

        if not log:
            # Pokud transakci nenajdeme, jen zalogujeme varování (nechceme shodit nabíječku)
            print(f"⚠️ StopTransaction pro neznámé ID: {data.transaction_id}")
            return {"status": "Ignored"}

        # 2. Výpočet spotřeby (Wh -> kWh)
        # Ošetření proti záporné spotřebě (pokud je elektroměr vadný)
        consumed_wh = max(0, data.meter_stop - log.meter_start)
        consumed_kwh = Decimal(consumed_wh) / Decimal(1000)

        # 3. Výpočet ceny
        # (Cena za kWh z DB * spotřeba)
        # Zde by se dalo přidat i účtování za čas (parking fee)
        total_price = consumed_kwh * log.price_per_kwh

        # 4. Aktualizace záznamu
        log.meter_stop = data.meter_stop
        log.end_time = data.timestamp
        log.energy_wh = consumed_wh
        log.price = round(total_price, 2)
        log.status = ChargeStatus.COMPLETED

        # 5. Stržení kreditu uživateli (pokud existuje)
        # TODO: Implementovat user.balance -= total_price

        await self._db.commit()
        return {"status": "Accepted"}