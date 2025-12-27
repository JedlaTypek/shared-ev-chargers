from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone

# Sloučené importy
from app.api.v1 import deps
from app.models.charger import (
    ChargerTechnicalStatus, 
    ChargerAuthorizeRequest,
    ChargerExistenceCheck,
    ChargerRead # Jen pro response model
)
from app.models.charge_log import (
    TransactionStartRequest,
    TransactionStopRequest,
    TransactionMeterValueRequest
)
from app.models.connector import ConnectorStatusUpdate
from app.services.charger_service import ChargerService
from app.services.connector_service import ConnectorService
from app.services.transaction_service import TransactionService
from app.api.v1.deps import get_connector_service
from app.api.v1.deps import get_charger_service
from app.api.v1.deps import get_transaction_service

# Zamkneme celý router na API Key
router = APIRouter(
    dependencies=[Depends(deps.verify_api_key)]
)

# --- OCPP Endpoints ---

@router.post("/heartbeat/{ocpp_id}")
async def handle_heartbeat(
    ocpp_id: str,
    service: ChargerService = Depends(deps.get_charger_service)
):
    # 1. Uložíme do Redisu
    await service.update_heartbeat(ocpp_id)
    
    # 2. Vrátíme aktuální čas serveru (UTC, Timezone Aware)
    return {
        "currentTime": datetime.now(timezone.utc).isoformat() # <--- OPRAVA
    }

@router.post("/boot-notification/{ocpp_id}", response_model=ChargerRead)
async def handle_boot_notification(
    ocpp_id: str,
    data: ChargerTechnicalStatus,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Voláno z Node.js při startu nabíječky.
    """
    charger = await service.update_technical_status(ocpp_id, data)
    
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not registered")
        
    return charger

@router.post("/authorize/{ocpp_id}")
async def authorize_charger(
    ocpp_id: str,
    auth_request: ChargerAuthorizeRequest,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Voláno z OCPP serveru při akci 'Authorize'.
    """
    id_tag_info = await service.authorize_tag(ocpp_id, auth_request.id_tag)
    return {"idTagInfo": id_tag_info}

@router.get("/authorized-tag/{ocpp_id}")
async def get_authorized_tag(
    ocpp_id: str,
    service: ChargerService = Depends(get_charger_service)
):
    """
    Vrátí poslední autorizovanou kartu pro danou nabíječku.
    """
    tag = await service.get_authorized_tag(ocpp_id)
    
    if not tag:
        raise HTTPException(status_code=404, detail="No authorized tag found (or expired)")
    
    return {"id_tag": tag}

@router.get("/charger/exists/{ocpp_id}", response_model=ChargerExistenceCheck)
async def check_charger_exists(
    ocpp_id: str, 
    service: ChargerService = Depends(get_charger_service)
):
    """
    Rychlé ověření pro handshake OCPP serveru.
    """
    charger = await service.check_exists_by_ocpp(ocpp_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    
    if not charger["is_active"]:
        raise HTTPException(status_code=403, detail="Charger is disabled")

    return charger

@router.post("/connector-status", status_code=status.HTTP_200_OK)
async def update_connector_status(
    status_data: ConnectorStatusUpdate,
    service: ConnectorService = Depends(get_connector_service) # Musíš si naimportovat get_connector_service nebo ho definovat i tady
):
    """
    Voláno z OCPP serveru (StatusNotification).
    Aktualizuje Redis status a případně vytvoří konektor v DB.
    """
    result = await service.process_status_notification(status_data)
    if not result:
        # Nabíječka s tímto OCPP ID nebyla nalezena
        return {"status": "ignored", "reason": "Charger not found"}
    
    return {"status": "updated", "connector_id": result.id}


@router.post("/transaction/start")
async def start_transaction(
    data: TransactionStartRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    tx_id = await service.start_transaction(data)
    return {"transactionId": tx_id}

@router.post("/transaction/stop")
async def stop_transaction(
    data: TransactionStopRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    return await service.stop_transaction(data)

@router.post("/transaction/meter-values")
async def process_meter_values(
    data: TransactionMeterValueRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    await service.process_meter_value(data)
    return {"status": "Accepted"}

@router.post("/transaction/prune")
async def prune_stale_transactions(
    service: TransactionService = Depends(get_transaction_service)
):
    """
    Úklid sirotků volaný CRONem (který musí mít API Key).
    """
    count = await service.close_stale_transactions(max_age_minutes=15)
    return {"message": f"Cleaned {count} stale transactions"}