from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.db.schema import Charger
from app.models.charger import ChargerCreate, ChargerUpdate

class ChargerService:
    def __init__(self, session: AsyncSession):
        self._db = session

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