from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from redis.asyncio import Redis

<<<<<<< HEAD
from app.db.schema import Charger
from app.models.charger import ChargerCreate, ChargerTechnicalStatus, ChargerUpdate
=======
from app.db.schema import Charger, RFIDCard
from app.models.charger import ChargerCreate, ChargerUpdate, ChargerAuthorizeRequest
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe

class ChargerService:
    def __init__(self, session: AsyncSession, redis: Redis = None):
        self._db = session
        self._redis = redis

    async def list_chargers(self, skip: int = 0, limit: int = 100) -> list[Charger]:
        stmt = select(Charger).options(selectinload(Charger.connectors)).offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_charger(self, charger_id: int) -> Charger | None:
        stmt = select(Charger).options(selectinload(Charger.connectors)).where(Charger.id == charger_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def create_charger(self, data: ChargerCreate) -> Charger:
        if data.ocpp_id:
            stmt = select(Charger).where(Charger.ocpp_id == data.ocpp_id)
            existing_result = await self._db.execute(stmt)
            existing = existing_result.scalars().first()
            if existing:
                raise ValueError(f"Charger with OCPP ID '{data.ocpp_id}' already exists")

        charger = Charger(
            owner_id=data.owner_id,
            name=data.name,
            latitude=data.latitude,
            longitude=data.longitude,
            street=data.street,
            house_number=data.house_number,
            city=data.city,
            postal_code=data.postal_code,
            region=data.region,
            ocpp_id=data.ocpp_id,
            is_active=data.is_active
        )
        
        self._db.add(charger)
        await self._db.commit()
        await self._db.refresh(charger)
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
    
<<<<<<< HEAD
    async def get_charger_by_ocpp_id(self, ocpp_id: str) -> Charger | None:
        """Najde nabíječku podle textového OCPP ID"""
        stmt = (
            select(Charger)
            .options(selectinload(Charger.connectors))
            .where(Charger.ocpp_id == ocpp_id)
        )
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def update_technical_status(self, ocpp_id: str, data: ChargerTechnicalStatus) -> Charger | None:
        """
        Aktualizuje metadata (firmware, model...) při startu nabíječky.
        Zároveň slouží jako ověření, že nabíječka existuje.
        """
        charger = await self.get_charger_by_ocpp_id(ocpp_id)
        
        if not charger:
            return None # Nabíječka neexistuje -> Odmítnout připojení
        
        # Aktualizujeme pouze pole, která přišla vyplněná
        if data.vendor: charger.vendor = data.vendor
        if data.model: charger.model = data.model
        if data.serial_number: charger.serial_number = data.serial_number
        if data.firmware_version: charger.firmware_version = data.firmware_version
        
        await self._db.commit()
        await self._db.refresh(charger)
        return charger
=======
    async def authorize_tag(self, ocpp_id: str, id_tag: str) -> dict:
        """
        Ověří kartu a pokud je platná, uloží ji dočasně do Redisu.
        """
        # A. Ověříme, zda existuje nabíječka
        charger = await self.get_charger_by_ocpp_id(ocpp_id)
        if not charger:
            # Nabíječka není v našem systému -> Ignorovat
            return {"status": "Invalid"}

        # B. Ověříme kartu v DB
        # Hledáme kartu podle UID
        stmt = select(RFIDCard).where(RFIDCard.card_uid == id_tag)
        result = await self._db.execute(stmt)
        card = result.scalars().first()

        if not card:
            # Karta neexistuje
            print(f"❌ Authorization failed: Unknown card {id_tag}")
            return {"status": "Invalid"}
        
        if not card.is_active:
            # Karta je zablokovaná
            print(f"🚫 Authorization failed: Card {id_tag} is blocked")
            return {"status": "Blocked"}

        # (Volitelně: Zde bychom mohli ověřit i zůstatek uživatele card.owner.balance)

        # C. Uložíme do Redisu (Pre-authorization)
        # Klíč: charger:{ocpp_id}:authorized_tag
        # TTL: 60 sekund (uživatel má minutu na to, aby připojil kabel)
        if self._redis:
            redis_key = f"charger:{ocpp_id}:authorized_tag"
            await self._redis.set(redis_key, id_tag, ex=60)
            print(f"🔐 Authorized tag {id_tag} on {ocpp_id} (TTL 60s)")

        # D. Vrátíme úspěch ve formátu pro OCPP
        return {
            "status": "Accepted",
            # "expiryDate": ..., # Volitelné
            # "parentIdTag": ... # Volitelné
        }

    async def get_authorized_tag(self, ocpp_id: str) -> str | None:
        """
        Získá aktuálně autorizovaný id_tag z Redisu pro danou nabíječku.
        Pokud klíč neexistuje (vypršel TTL 60s), vrátí None.
        """
        if not self._redis:
            return None
            
        redis_key = f"charger:{ocpp_id}:authorized_tag"
        tag = await self._redis.get(redis_key)
        return tag
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
