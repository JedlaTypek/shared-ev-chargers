from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.deps import get_transaction_service, get_current_user
from app.services.transaction_service import TransactionService
from app.models.charge_log import ChargeLogRead # Budeme potřebovat Read model
from app.db.schema import User
from app.models.enums import UserRole

router = APIRouter()

@router.get("/", response_model=list[ChargeLogRead])
async def get_my_transactions(
    skip: int = 0,
    limit: int = 50,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
):
    """
    Zobrazí historii nabíjení.
    - Admin vidí vše.
    - Uživatel vidí jen své.
    """
    if current_user.role == UserRole.admin:
        return await service.get_transactions(skip=skip, limit=limit)
    else:
        return await service.get_transactions(user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{transaction_id}", response_model=ChargeLogRead)
async def get_transaction_detail(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
):
    tx = await service.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # Kontrola oprávnění
    is_admin = current_user.role == UserRole.admin
    if tx.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return tx