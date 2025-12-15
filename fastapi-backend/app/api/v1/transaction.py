from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db
from app.services.transaction_service import TransactionService
from app.models.charge_log import TransactionStartRequest, TransactionStopRequest

router = APIRouter()

def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    return TransactionService(session=db)

@router.post("/start")
async def start_transaction(
    data: TransactionStartRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    tx_id = await service.start_transaction(data)
    return {"transactionId": tx_id}

@router.post("/stop")
async def stop_transaction(
    data: TransactionStopRequest,
    service: TransactionService = Depends(get_transaction_service)
):
    return await service.stop_transaction(data)