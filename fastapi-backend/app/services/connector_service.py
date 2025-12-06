from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis # Async redis

from app.db.schema import Connector, Charger
from app.models.connector import ConnectorCreate, ConnectorStatusUpdate, ConnectorRead

class ConnectorService:
    def __init__(self, session: AsyncSession, redis: Redis):
        self._db = session
        self._redis = redis

    def _get_redis_key(self, ocpp_id: str, connector_num: int) -> str:
        return f"charger:{ocpp_id}:connector:{connector_num}:status"

    async def process_status_notification(self, data: ConnectorStatusUpdate) -> Connector | None:
        # 1. Redis - await
        redis_key = self._get_redis_key(data.ocpp_id, data.connector_number)
        await self._redis.set(redis_key, data.status, ex=86400)

        # 2. DB - await
        stmt_charger = select(Charger).where(Charger.ocpp_id == data.ocpp_id)
        result_charger = await self._db.execute(stmt_charger)
        charger = result_charger.scalars().first()
        
        if not charger:
            return None

        stmt_connector = select(Connector).where(
            Connector.charger_id == charger.id,
            Connector.ocpp_number == data.connector_number
        )
        result_connector = await self._db.execute(stmt_connector)
        connector = result_connector.scalars().first()

        if not connector:
            print(f"✨ Auto-discovering new connector #{data.connector_number}")
            connector = Connector(
                charger_id=charger.id,
                ocpp_number=data.connector_number,
                is_active=False
            )
            self._db.add(connector)
            await self._db.commit() # await commit
            await self._db.refresh(connector) # await refresh
        
        return connector

    async def get_connector_with_status(self, connector_id: int) -> ConnectorRead | None:
        # Join v async vyžaduje explicitní načtení nebo join v dotazu
        stmt = select(Connector, Charger.ocpp_id).join(Charger).where(Connector.id == connector_id)
        result = await self._db.execute(stmt)
        row = result.first()
        
        if not row:
            return None
            
        connector, ocpp_id = row
        
        redis_key = self._get_redis_key(ocpp_id, connector.ocpp_number)
        status = await self._redis.get(redis_key)
        
        response_model = ConnectorRead.model_validate(connector)
        response_model.status = status if status else "Unknown"
        return response_model