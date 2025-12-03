from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.schema import Charger
from app.models.charger import ChargerCreate, ChargerUpdate

class ChargerService:
    def __init__(self, session: Session):
        self._db = session

    def list_chargers(self, skip: int = 0, limit: int = 100) -> list[Charger]:
        # Eager loading konektorů, abychom je viděli ve výstupu
        stmt = select(Charger).options(selectinload(Charger.connectors)).offset(skip).limit(limit)
        result = self._db.execute(stmt)
        return result.scalars().all()

    def get_charger(self, charger_id: int) -> Charger | None:
        stmt = select(Charger).options(selectinload(Charger.connectors)).where(Charger.id == charger_id)
        return self._db.execute(stmt).scalars().first()

    def create_charger(self, data: ChargerCreate) -> Charger:
        # Kontrola unikátnosti OCPP ID
        if data.ocpp_id:
            existing = self._db.execute(select(Charger).where(Charger.ocpp_id == data.ocpp_id)).scalars().first()
            if existing:
                raise ValueError(f"Charger with OCPP ID '{data.ocpp_id}' already exists")

        charger = Charger(
            owner_id=data.owner_id, # Dočasně bereme z inputu
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
        self._db.commit()
        self._db.refresh(charger)
        return charger

    def update_charger(self, charger_id: int, data: ChargerUpdate) -> Charger | None:
        charger = self.get_charger(charger_id)
        if not charger:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(charger, key, value)

        self._db.commit()
        self._db.refresh(charger)
        return charger

    def delete_charger(self, charger_id: int) -> bool:
        charger = self.get_charger(charger_id)
        if not charger:
            return False
        
        self._db.delete(charger)
        self._db.commit()
        return True