from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.v1.deps import get_db, get_redis
from app.models.connector import ConnectorStatusUpdate, ConnectorRead
from app.services.connector_service import ConnectorService

router = APIRouter()

def get_connector_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ConnectorService:
    return ConnectorService(session=db, redis=redis)

@router.post("/ocpp-status", status_code=status.HTTP_200_OK)
async def update_ocpp_status( # ZMĚNA: async def
    status_data: ConnectorStatusUpdate,
    service: ConnectorService = Depends(get_connector_service)
):
    # ZMĚNA: await
    result = await service.process_status_notification(status_data)
    if not result:
        return {"status": "ignored", "reason": "Charger not found"}
    return {"status": "updated", "connector_id": result.id}

@router.get("/{connector_id}", response_model=ConnectorRead)
async def get_connector( # ZMĚNA: async def
    connector_id: int,
    service: ConnectorService = Depends(get_connector_service)
):
    # ZMĚNA: await
    connector = await service.get_connector_with_status(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector