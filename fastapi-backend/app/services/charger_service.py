from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, attributes
from sqlalchemy import select
from redis.asyncio import Redis

# Sloučené importy z obou větví
from app.db.schema import Charger, RFIDCard
from app.models.charger import (
    ChargerCreate, 
    ChargerUpdate, 
    ChargerTechnicalStatus
)

class ChargerService:
    def __init__(self, session: AsyncSession, redis: Redis = None):
        self._db = session
        self._redis = redis

    # ZMĚNA: Přidán parametr owner_id pro filtrování (Moje nabíječky)
    async def list_chargers(self, skip: int = 0, limit: int = 100, owner_id: int | None = None) -> list[Charger]:
        stmt = select(Charger).options(selectinload(Charger.connectors))
        
        if owner_id:
            stmt = stmt.where(Charger.owner_id == owner_id)
            
        stmt = stmt.offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_charger(self, charger_id: int) -> Charger | None:
        stmt = select(Charger).options(selectinload(Charger.connectors)).where(Charger.id == charger_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def _generate_ocpp_id(self, prefix: str = "CZ-ECLD") -> str:
        stmt = (
            select(Charger.ocpp_id)
            .where(Charger.ocpp_id.like(f"{prefix}-%"))
            .order_by(Charger.ocpp_id.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        last_id = result.scalars().first()

        new_number = 1
        if last_id:
            try:
                number_part = last_id.split('-')[-1]
                new_number = int(number_part) + 1
            except ValueError:
                new_number = 1

        return f"{prefix}-{str(new_number).zfill(6)}"

    async def create_charger(self, data: ChargerCreate) -> Charger:
        new_ocpp_id = await self._generate_ocpp_id()

        charger = Charger(
            owner_id=data.owner_id, # Toto už musí být validní ID (nastavené v routeru)
            name=data.name,
            latitude=data.latitude,
            longitude=data.longitude,
            street=data.street,
            house_number=data.house_number,
            city=data.city,
            postal_code=data.postal_code,
            region=data.region,
            ocpp_id=new_ocpp_id, 
            is_active=data.is_active
        )

        self._db.add(charger)
        await self._db.commit()
        await self._db.refresh(charger)
        
        attributes.set_committed_value(charger, "connectors", [])
        return charger

    async def update_charger(self, charger_id: int, data: ChargerUpdate) -> Charger | None:
        charger = await self.get_charger(charger_id)
        if not charger:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(charger, key, value)

        await self._db.commit()
        await self._db.refresh(charger)
        return charger

    async def delete_charger(self, charger_id: int) -> bool:
        charger = await self.get_charger(charger_id)
        if not charger:
            return False
        
        await self._db.delete(charger)
        await self._db.commit()
        return True
    
    # --- Metody pro BootNotification / Auto-discovery ---

    async def get_charger_by_ocpp_id(self, ocpp_id: str) -> Charger | None:
        stmt = (
            select(Charger)
            .options(selectinload(Charger.connectors))
            .where(Charger.ocpp_id == ocpp_id)
        )
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def update_technical_status(self, ocpp_id: str, data: ChargerTechnicalStatus) -> Charger | None:
        charger = await self.get_charger_by_ocpp_id(ocpp_id)
        if not charger:
            return None 
        
        if data.vendor: charger.vendor = data.vendor
        if data.model: charger.model = data.model
        if data.serial_number: charger.serial_number = data.serial_number
        if data.firmware_version: charger.firmware_version = data.firmware_version
        
        await self._db.commit()
        await self._db.refresh(charger)
        return charger

    # --- Metody pro Authorize (RFID) ---

    async def authorize_tag(self, ocpp_id: str, id_tag: str) -> dict:
        charger = await self.get_charger_by_ocpp_id(ocpp_id)
        if not charger:
            return {"status": "Invalid"}

        stmt = select(RFIDCard).where(RFIDCard.card_uid == id_tag)
        result = await self._db.execute(stmt)
        card = result.scalars().first()

        if not card:
            print(f"❌ Authorization failed: Unknown card {id_tag}")
            return {"status": "Invalid"}
        
        if not card.is_active:
            print(f"🚫 Authorization failed: Card {id_tag} is blocked")
            return {"status": "Blocked"}

        if self._redis:
            redis_key = f"charger:{ocpp_id}:authorized_tag"
            await self._redis.set(redis_key, id_tag, ex=60)
            print(f"🔐 Authorized tag {id_tag} on {ocpp_id} (TTL 60s)")

        return {"status": "Accepted"}

    async def get_authorized_tag(self, ocpp_id: str) -> str | None:
        if not self._redis:
            return None
        redis_key = f"charger:{ocpp_id}:authorized_tag"
        tag = await self._redis.get(redis_key)
        return tag
    
    async def check_exists_by_ocpp(self, ocpp_id: str) -> dict | None:
        stmt = select(Charger.id, Charger.is_active).where(Charger.ocpp_id == ocpp_id)
        result = await self._db.execute(stmt)
        row = result.first()
        if row:
            return {"id": row.id, "is_active": row.is_active}
        return None