from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

# Sloučené importy
from app.api.v1.deps import get_db, get_redis, get_current_user, get_charger_service, get_current_user_optional
from app.models.charger import (
    ChargerCreate,
    ChargerExistenceCheck, 
    ChargerRead, 
    ChargerUpdate, 
    ChargerTechnicalStatus, 
    ChargerAuthorizeRequest
)
from app.models.enums import UserRole
from app.db.schema import User 
from app.services.charger_service import ChargerService

router = APIRouter()

# --- GET CHARGERS (Public / Private) ---
@router.get("", response_model=list[ChargerRead])
async def get_chargers(
    mine: bool = False, # ?mine=true (přepínač)
    service: ChargerService = Depends(get_charger_service),
    # ZMĚNA ZDE: Použijeme optional verzi. 
    # Pokud uživatel nemá token, current_user bude None, ale nevyhodí to chybu 401.
    current_user: User | None = Depends(get_current_user_optional) 
):
    # Logika pro filtrování "jen moje"
    if mine:
        # Pokud chce uživatel "svoje" nabíječky, ale není přihlášený -> CHYBA
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Authentication required for 'mine' filter"
            )
        return await service.list_chargers(owner_id=current_user.id)
    
    # Veřejný seznam všech nabíječek (dostupný i pro current_user=None)
    return await service.list_chargers()


# --- CREATE CHARGER (Protected: Owner or Admin) ---
@router.post("", response_model=ChargerRead, status_code=status.HTTP_201_CREATED)
async def create_charger(
    charger_data: ChargerCreate,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    # 1. KONTROLA ROLE: Jen Owner nebo Admin může vytvářet nabíječky
    if current_user.role not in [UserRole.owner, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only approved Owners or Admins can create chargers. Please upgrade your account."
        )

    # 2. NASTAVENÍ VLASTNÍKA (ID z tokenu)
    # Pokud není admin, nabíječka patří tomu, kdo ji vytváří.
    if current_user.role != UserRole.admin:
        charger_data.owner_id = current_user.id
    else:
        # Admin může v JSONu poslat owner_id a vytvořit nabíječku pro někoho jiného.
        # Pokud ho nepošle, přiřadíme ji adminovi.
        if not charger_data.owner_id:
            charger_data.owner_id = current_user.id

    try:
        return await service.create_charger(charger_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- GET CHARGER DETAIL ---
@router.get("/{charger_id}", response_model=ChargerRead)
async def get_charger(
    charger_id: int, 
    service: ChargerService = Depends(get_charger_service)
):
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger


# --- UPDATE CHARGER (Protected: My Charger or Admin) ---
@router.patch("/{charger_id}", response_model=ChargerRead)
async def update_charger(
    charger_id: int,
    charger_update: ChargerUpdate,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    # 1. Načteme existující nabíječku
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    # 2. KONTROLA OPRÁVNĚNÍ: Je to moje nabíječka? Nebo jsem Admin?
    is_owner = charger.owner_id == current_user.id
    is_admin = current_user.role == UserRole.admin

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to update this charger."
        )

    # 3. Provedeme update
    updated = await service.update_charger(charger_id, charger_update)
    return updated


# --- DELETE CHARGER (Protected: My Charger or Admin) ---
@router.delete("/{charger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_charger(
    charger_id: int,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    # 1. Načteme existující nabíječku
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    # 2. KONTROLA OPRÁVNĚNÍ
    is_owner = charger.owner_id == current_user.id
    is_admin = current_user.role == UserRole.admin

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to delete this charger."
        )

    # 3. Smazání
    await service.delete_charger(charger_id)
    return
