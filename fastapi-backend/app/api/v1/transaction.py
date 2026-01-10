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
    charger_id: int | None = None,
    as_owner: bool = False,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
):
    """
    Zobrazí historii nabíjení.
    - Admin vidí vše.
    - Owner může vidět logy svých nabíječek (as_owner=True).
    - Uživatel vidí jen své.
    """
    if current_user.role == UserRole.admin:
        return await service.get_transactions(skip=skip, limit=limit, charger_id=charger_id)
    
    if current_user.role == UserRole.owner and as_owner:
        return await service.get_transactions(owner_id=current_user.id, charger_id=charger_id, skip=skip, limit=limit)

    return await service.get_transactions(user_id=current_user.id, charger_id=charger_id, skip=skip, limit=limit)

@router.get("/usage", response_model=list[ChargeLogRead])
async def get_charger_usage(
    charger_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
):
    """
    Zobrazí historii využití nabíječek (pro Ownera nebo Admina).
    """
    # 1. Admin vidí vše (mohu filtrovat podle charger_id)
    if current_user.role == UserRole.admin:
        return await service.get_transactions(charger_id=charger_id, skip=skip, limit=limit)

    # 2. Owner vidí historii SWÝCH nabíječek
    if current_user.role == UserRole.owner:
        # Pokud zadal charger_id, musíme ověřit, že je JEHO?
        # Service.get_transactions s owner_id filtrem zajistí,
        # že se vrátí logy jen z nabíječek, které patří tomuto ownerovi.
        # Takže i když pošle cizí charger_id, vrátí to prázdný list (protože join Charger on owner_id).
        return await service.get_transactions(owner_id=current_user.id, charger_id=charger_id, skip=skip, limit=limit)

    # 3. Běžný uživatel nemá přístup k "usage" nabíječek (vidí jen své transakce v get_my_transactions)
    raise HTTPException(status_code=403, detail="Not authorized to view charger usage")

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