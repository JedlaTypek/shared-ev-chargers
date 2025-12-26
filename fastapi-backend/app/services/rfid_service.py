from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schema import RFIDCard
from app.models.rfid import RFIDCardCreate

class RFIDService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def list_cards(self, owner_id: int | None = None, show_all: bool = False) -> list[RFIDCard]:
        stmt = select(RFIDCard)
        
        # Filtrování podle vlastníka
        if owner_id:
            stmt = stmt.where(RFIDCard.owner_id == owner_id)
        
        # Filtrování smazaných (pokud nechceme zobrazit vše)
        if not show_all:
            stmt = stmt.where(RFIDCard.is_active == True) # noqa: E712

        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def create_card(self, card_data: RFIDCardCreate, owner_id: int) -> RFIDCard:
        # Kontrola unikátnosti UID (musíme zkontrolovat i mezi neaktivními, 
        # protože fyzická karta s tímto UID stále existuje)
        existing_card = await self.get_card_by_uid(card_data.card_uid)
        
        if existing_card:
            # Pokud karta existuje a je smazaná, mohli bychom ji reaktivovat,
            # ale pro jednoduchost zatím vyhodíme chybu.
            raise ValueError("Card UID already registered")

        card = RFIDCard(
            card_uid=card_data.card_uid,
            owner_id=owner_id,
            is_active=True
        )
        
        self._db.add(card)
        await self._db.commit()
        await self._db.refresh(card)
        return card

    async def get_card(self, card_id: int) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.id == card_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def get_card_by_uid(self, uid: str) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.card_uid == uid)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    # --- SOFT DELETE ---
    async def delete_card(self, card_id: int) -> bool:
        card = await self.get_card(card_id)
        if not card:
            return False
        
        # Místo smazání jen nastavíme příznak
        card.is_active = False
        
        await self._db.commit()
        return True