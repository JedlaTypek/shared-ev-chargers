from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.v1.deps import get_db, get_redis, get_current_user
from app.models.charger import ChargerCreate, ChargerRead, ChargerUpdate
from app.services.charger_service import ChargerService
from app.db.schema import User
from app.models.enums import UserRole
from app.api.v1.deps import get_charger_service

router = APIRouter()

# --- GET CHARGERS (Public / Private) ---
@router.get("/", response_model=list[ChargerRead])
async def get_chargers(
    mine: bool = False, # ?mine=true (jen moje)
    service: ChargerService = Depends(get_charger_service),
    # Volitelně uživatel (pokud chce filtrovat "moje", musí být přihlášen)
    # Pro veřejnou mapu nemusí být přihlášen
    current_user: User | None = Depends(get_current_user) # Tady možná použít optional, pokud máš
):
    # Pokud uživatel chce vidět jen svoje, musí být přihlášen
    if mine:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required for 'mine' filter")
        return await service.list_chargers(owner_id=current_user.id)
    
    # Jinak vrátíme všechny (veřejná mapa)
    return await service.list_chargers()

# --- CREATE CHARGER (Protected) ---
@router.post("/", response_model=ChargerRead, status_code=status.HTTP_201_CREATED)
async def create_charger(
    charger_data: ChargerCreate,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    try:
        # Logika: Admin může vytvořit nabíječku komukoliv.
        # Běžný uživatel jen sobě.
        is_admin = current_user.role == UserRole.admin
        
        if not is_admin:
            # Vynutíme ID vlastníka na aktuálního uživatele
            charger_data.owner_id = current_user.id
            # Běžný user nemůže hned aktivovat, pokud by to podléhalo schválení (volitelné)
            # charger_data.is_active = True 
        
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

# --- UPDATE CHARGER (Protected) ---
@router.patch("/{charger_id}", response_model=ChargerRead)
async def update_charger(
    charger_id: int,
    charger_update: ChargerUpdate,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    # 1. Najít nabíječku
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    # 2. Kontrola oprávnění (Vlastník nebo Admin)
    is_admin = current_user.role == UserRole.admin
    if charger.owner_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Update
    updated = await service.update_charger(charger_id, charger_update)
    return updated

# --- DELETE CHARGER (Protected) ---
@router.delete("/{charger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_charger(
    charger_id: int,
    service: ChargerService = Depends(get_charger_service),
    current_user: User = Depends(get_current_user)
):
    # 1. Najít nabíječku
    charger = await service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    # 2. Kontrola oprávnění
    is_admin = current_user.role == UserRole.admin
    if charger.owner_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Delete
    await service.delete_charger(charger_id)
    return