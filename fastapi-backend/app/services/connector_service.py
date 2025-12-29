from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.db.schema import Connector, Charger
from app.models.connector import ConnectorStatusUpdate, ConnectorRead, ConnectorUpdate

class ConnectorService:
    def __init__(self, session: AsyncSession, redis: Redis):
        self._db = session
        self._redis = redis

    def _get_redis_key(self, ocpp_id: str, connector_num: int) -> str:
        return f"charger:{ocpp_id}:connector:{connector_num}:status"

    # --- POUŽÍVÁ INTERNAL API (OCPP) ---
    async def process_status_notification(self, data: ConnectorStatusUpdate) -> Connector | None:
        # 1. Uložíme status do Redisu (Expirace 24h)
        redis_key = self._get_redis_key(data.ocpp_id, data.connector_number)
        await self._redis.set(redis_key, data.status, ex=86400)

        # 2. Najdeme nabíječku
        stmt_charger = select(Charger).where(Charger.ocpp_id == data.ocpp_id)
        result_charger = await self._db.execute(stmt_charger)
        charger = result_charger.scalars().first()
        
        if not charger:
            return None

        # 3. Najdeme nebo vytvoříme konektor (Auto-discovery)
        stmt_connector = select(Connector).where(
            Connector.charger_id == charger.id,
            Connector.ocpp_number == data.connector_number
        )
        result_connector = await self._db.execute(stmt_connector)
        connector = result_connector.scalars().first()

        if not connector:
            print(f"✨ Auto-discovering new connector #{data.connector_number} for {data.ocpp_id}")
            connector = Connector(
                charger_id=charger.id,
                ocpp_number=data.connector_number,
                is_active=False # Nový konektor musí majitel nejdřív nastavit a aktivovat
            )
            self._db.add(connector)
            await self._db.commit()
            await self._db.refresh(connector)
        
        return connector

    # --- POMOCNÁ METODA PRO FETCH DB OBJEKTU ---
    async def get_connector(self, connector_id: int) -> Connector | None:
        """Vrání ORM objekt včetně načtené relace Charger (pro kontrolu majitele)."""
        stmt = (
            select(Connector)
            .options(selectinload(Connector.charger)) # Důležité pro charger.owner_id
            .where(Connector.id == connector_id)
        )
        result = await self._db.execute(stmt)
        return result.scalars().first()

    # --- POUŽÍVÁ USER API ---
    async def get_connector_with_status(self, connector_id: int) -> ConnectorRead | None:
        # Získáme konektor i s nabíječkou
        connector = await self.get_connector(connector_id)
        
        if not connector:
            return None
            
        # Dotaz do Redisu pro aktuální status
        redis_key = self._get_redis_key(connector.charger.ocpp_id, connector.ocpp_number)
        status = await self._redis.get(redis_key)
        
        # Převedeme na Pydantic a doplníme status
        response_model = ConnectorRead.model_validate(connector)
        response_model.status = status if status else "Unknown"
        return response_model
    
    async def update_connector(self, connector_id: int, data: ConnectorUpdate) -> Connector | None:
        connector = await self.get_connector(connector_id)
        if not connector:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(connector, key, value)

        await self._db.commit()
        await self._db.refresh(connector)
        return connector

    async def get_by_ocpp_ids(self, identity: str, ocpp_connector_id: int):
        """
        Najde konektor podle identity nabíječky (z URL) a čísla konektoru.
        Předpokládáme, že 'identity' v URL odpovídá 'serial_number' v DB.
        """
        query = (
            select(Connector)
            .join(Charger)
            .where(Charger.serial_number == identity)  # Zde mapujeme Identity -> SerialNumber
            .where(Connector.connector_id == ocpp_connector_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()