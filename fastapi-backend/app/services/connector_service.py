from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.schema import Connector
from app.models.connector import ConnectorCreate, ConnectorUpdate

class ConnectorService:
    def __init__(self, session: Session):
        self._db = session

    def get_connector(self, connector_id: int) -> Connector | None:
        stmt = select(Connector).where(Connector.id == connector_id)
        return self._db.execute(stmt).scalars().first()

    def create_connector(self, data: ConnectorCreate) -> Connector:
        # Kontrola duplicity čísla konektoru na stejné nabíječce
        stmt = select(Connector).where(
            Connector.charger_id == data.charger_id,
            Connector.ocpp_number == data.ocpp_number
        )
        existing = self._db.execute(stmt).scalars().first()
        if existing:
            raise ValueError(f"Connector #{data.ocpp_number} already exists on charger {data.charger_id}")

        connector = Connector(
            charger_id=data.charger_id,
            ocpp_number=data.ocpp_number,
            type=data.type,
            current_type=data.current_type,
            max_power_w=data.max_power_w,
            price_per_kwh=data.price_per_kwh,
            is_active=data.is_active
        )
        
        self._db.add(connector)
        self._db.commit()
        self._db.refresh(connector)
        return connector

    def delete_connector(self, connector_id: int) -> bool:
        connector = self.get_connector(connector_id)
        if not connector:
            return False
        self._db.delete(connector)
        self._db.commit()
        return True