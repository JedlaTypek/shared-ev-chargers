from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.v1.deps import get_db, get_redis, get_current_user
from app.models.connector import ConnectorRead, ConnectorUpdate
from app.services.connector_service import ConnectorService
from app.db.schema import User
from app.models.enums import UserRole
from app.api.v1.deps import get_connector_service

router = APIRouter()

@router.get("/{connector_id}", response_model=ConnectorRead)
async def get_connector(
    connector_id: int,
    service: ConnectorService = Depends(get_connector_service)
):
    # Tento endpoint může být veřejný (pro detail nabíječky na mapě),
    # nebo chráněný. Zatím necháváme veřejný.
    connector = await service.get_connector_with_status(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.patch("/{connector_id}", response_model=ConnectorRead)
async def update_connector(
    connector_id: int,
    connector_update: ConnectorUpdate,
    service: ConnectorService = Depends(get_connector_service),
    current_user: User = Depends(get_current_user) # Vyžaduje přihlášení
):
    """
    Klíčový endpoint pro majitele:
    Doplní cenu/výkon a aktivuje konektor.
    """
    # 1. Načteme konektor (abychom zjistili majitele nabíječky)
    connector_orm = await service.get_connector(connector_id)
    if not connector_orm:
        raise HTTPException(status_code=404, detail="Connector not found")

    # 2. Kontrola oprávnění (Vlastník nabíječky nebo Admin)
    # Díky selectinload v service můžeme přistoupit k .charger.owner_id
    is_owner = connector_orm.charger.owner_id == current_user.id
    is_admin = current_user.role == UserRole.admin

    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Update
    updated = await service.update_connector(connector_id, connector_update)
    
    # 4. Vrácení výsledku i se statusem z Redisu
    return await service.get_connector_with_status(connector_id)

@router.get("/ocpp/{identity}/{ocpp_connector_id}", response_model=ConnectorRead)
async def get_connector_by_ocpp_data(
    identity: str,
    ocpp_connector_id: int,
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Voláno z Node.js backendu. 'identity' je ID z WebSocket URL.
    """
    connector = await service.get_by_ocpp_ids(identity, ocpp_connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector