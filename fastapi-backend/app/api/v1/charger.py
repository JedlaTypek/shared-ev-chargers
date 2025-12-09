from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

<<<<<<< HEAD
from app.api.v1.deps import get_db
from app.models.charger import ChargerCreate, ChargerRead, ChargerTechnicalStatus, ChargerUpdate
=======
from app.api.v1.deps import get_db, get_redis
from app.models.charger import ChargerCreate, ChargerRead, ChargerUpdate, ChargerAuthorizeRequest, ChargerTechnicalStatus
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
from app.services.charger_service import ChargerService

router = APIRouter()

def get_charger_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ChargerService:
    return ChargerService(session=db, redis=redis)

@router.get("", response_model=list[ChargerRead])
async def get_chargers(service: ChargerService = Depends(get_charger_service)):
    return await service.list_chargers()

@router.post("", response_model=ChargerRead, status_code=status.HTTP_201_CREATED)
async def create_charger(
    charger_data: ChargerCreate,
    service: ChargerService = Depends(get_charger_service)
):
    try:
        return await service.create_charger(charger_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{charger_id}", response_model=ChargerRead)
async def get_charger(
    charger_id: int, 
    service: ChargerService = Depends(get_charger_service)
):
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger

@router.patch("/{charger_id}", response_model=ChargerRead)
async def update_charger(
    charger_id: int,
    charger_update: ChargerUpdate,
    service: ChargerService = Depends(get_charger_service)
):
    updated = await service.update_charger(charger_id, charger_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Charger not found")
    return updated

@router.delete("/{charger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_charger(
    charger_id: int,
    service: ChargerService = Depends(get_charger_service)
):
    success = await service.delete_charger(charger_id)
    if not success:
        raise HTTPException(status_code=404, detail="Charger not found")
    return

<<<<<<< HEAD
# Endpoint pro OCPP Server (Webhook)
@router.post("/boot-notification/{ocpp_id}", response_model=ChargerRead)
async def handle_boot_notification(
    ocpp_id: str,
    data: ChargerTechnicalStatus,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Voláno z Node.js při startu nabíječky.
    Ověří existenci a uloží technická data.
    """
    charger = await service.update_technical_status(ocpp_id, data)
    
    if not charger:
        # 404 vrátí Node.js serveru signál, že má poslat "Rejected"
        raise HTTPException(status_code=404, detail="Charger not registered")
        
    return charger
=======
@router.post("/authorize/{ocpp_id}")
async def authorize_charger(
    ocpp_id: str,
    auth_request: ChargerAuthorizeRequest,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Voláno z OCPP serveru při akci 'Authorize'.
    1. Ověří kartu v DB.
    2. Uloží autorizaci do Redisu (cache).
    3. Vrátí status (Accepted/Invalid/Blocked).
    """
    # service.authorize_tag vrací dict {status: "..."}
    id_tag_info = await service.authorize_tag(ocpp_id, auth_request.id_tag)
    
    # Zabalíme to do idTagInfo, jak to očekává OCPP logika
    return {"idTagInfo": id_tag_info}

@router.get("/authorized-tag/{ocpp_id}")
async def get_authorized_tag(
    ocpp_id: str,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Vrátí poslední autorizovanou kartu pro danou nabíječku,
    pokud ještě nevypršel její časový limit (60s).
    """
    tag = await service.get_authorized_tag(ocpp_id)
    
    if not tag:
        # Pokud v Redisu nic není (nikdo nepípl nebo už to vypršelo)
        raise HTTPException(status_code=404, detail="No authorized tag found (or expired)")
    
    return {"id_tag": tag}
>>>>>>> 6fefceb4222a1a64705e382b46671648a9cf5ffe
