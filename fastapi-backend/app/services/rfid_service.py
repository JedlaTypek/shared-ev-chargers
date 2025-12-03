from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.schema import RFIDCard
from app.models.rfid import RFIDCardCreate, RFIDCardUpdate

class RFIDService:
    def __init__(self, session: Session):
        self._db = session

    def list_cards(self, skip: int = 0, limit: int = 100) -> list[RFIDCard]:
        stmt = select(RFIDCard).offset(skip).limit(limit)
        result = self._db.execute(stmt)
        return result.scalars().all()

    def get_card(self, card_id: int) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.id == card_id)
        return self._db.execute(stmt).scalars().first()

    # --- TUTO METODU BUDEŠ POTŘEBOVAT PRO OCPP ---
    def get_card_by_uid(self, card_uid: str) -> RFIDCard | None:
        stmt = select(RFIDCard).where(RFIDCard.card_uid == card_uid)
        return self._db.execute(stmt).scalars().first()

    def create_card(self, data: RFIDCardCreate) -> RFIDCard:
        # 1. Kontrola, jestli už karta s tímto UID neexistuje
        if self.get_card_by_uid(data.card_uid):
            raise ValueError(f"RFID Card with UID '{data.card_uid}' already exists")

        card = RFIDCard(
            card_uid=data.card_uid,
            owner_id=data.owner_id,
            is_active=data.is_active
        )
        
        self._db.add(card)
        self._db.commit()
        self._db.refresh(card)
        return card

    def update_card(self, card_id: int, data: RFIDCardUpdate) -> RFIDCard | None:
        card = self.get_card(card_id)
        if not card:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        self._db.commit()
        self._db.refresh(card)
        return card

    def delete_card(self, card_id: int) -> bool:
        card = self.get_card(card_id)
        if not card:
            return False
        
        self._db.delete(card)
        self._db.commit()
        return True