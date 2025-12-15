from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db
from app.services.transaction_service import TransactionService
from app.models.charge_log import TransactionStartRequest, TransactionStopRequest

router = APIRouter()

def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    return TransactionService(session=db)

@router.post("/start")
async def start_transaction_endpoint(
    data: TransactionStartRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    """Voláno z OCPP při StartTransaction"""
    transaction_id = await service.start_transaction(data)
    # Vrátíme transactionId, které nabíječka musí použít pro StopTransaction
    return {"transactionId": transaction_id}

@router.post("/stop")
async def stop_transaction_endpoint(
    data: TransactionStopRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    """Voláno z OCPP při StopTransaction"""
    result = await service.stop_transaction(data)
    return result