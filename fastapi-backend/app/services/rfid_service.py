from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schema import RFIDCard
from app.models.rfid import RFIDCardCreate, RFIDCardUpdate

class RFIDService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def list_cards(self, skip: int = 0, limit: int = 100) -> list[RFIDCard]:
        stmt = select(RFIDCard).offset(skip).limit(limit)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_card(self, card_id: int) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.id == card_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def get_card_by_uid(self, card_uid: str) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.card_uid == card_uid)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def create_card(self, data: RFIDCardCreate) -> RFIDCard:
        # Await volání vlastní metody
        if await self.get_card_by_uid(data.card_uid):
            raise ValueError(f"RFID Card with UID '{data.card_uid}' already exists")

        card = RFIDCard(
            card_uid=data.card_uid,
            owner_id=data.owner_id,
            is_active=data.is_active
        )
        
        self._db.add(card)
        await self._db.commit()
        await self._db.refresh(card)
        return card

    async def update_card(self, card_id: int, data: RFIDCardUpdate) -> RFIDCard | None:
        card = await self.get_card(card_id)
        if not card:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        await self._db.commit()
        await self._db.refresh(card)
        return card

    async def delete_card(self, card_id: int) -> bool:
        card = await self.get_card(card_id)
        if not card:
            return False
        
        await self._db.delete(card)
        await self._db.commit()
        return True