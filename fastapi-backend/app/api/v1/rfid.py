from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import deps
from app.models.rfid import RFIDCardCreate, RFIDCardRead
from app.services.rfid_service import RFIDService
from app.db.schema import User
from app.models.enums import UserRole

router = APIRouter()

def get_rfid_service(db: AsyncSession = Depends(deps.get_db)) -> RFIDService:
    return RFIDService(session=db)

# --- LIST CARDS ---
@router.get("/", response_model=list[RFIDCardRead])
async def get_cards(
    show_all: bool = False,  # ?show_all=true zobrazí i smazané
    service: RFIDService = Depends(get_rfid_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Admin vidí všechny karty (volitelně i smazané).
    Běžný uživatel vidí jen své karty (volitelně i smazané).
    """
    if current_user.role == UserRole.admin:
        # Admin vidí vše (pokud nezadá owner_id filtr, vidí karty všech lidí)
        return await service.list_cards(owner_id=None, show_all=show_all)
    else:
        # User vidí jen svoje
        return await service.list_cards(owner_id=current_user.id, show_all=show_all)

# --- CREATE CARD ---
@router.post("/", response_model=RFIDCardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: RFIDCardCreate,
    service: RFIDService = Depends(get_rfid_service),
    current_user: User = Depends(deps.get_current_user)
):
    try:
        # Tady je prostor pro logiku "Admin může vytvořit kartu komukoliv".
        # Zatím to necháme tak, že se karta tvoří pro current_user.
        # Pokud bys to chtěl rozšířit, musel bys v card_data poslat owner_id 
        # a zkontrolovat, zda je current_user Admin.
        
        return await service.create_card(card_data, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- GET CARD DETAIL ---
@router.get("/{card_id}", response_model=RFIDCardRead)
async def get_card(
    card_id: int, 
    service: RFIDService = Depends(get_rfid_service),
    current_user: User = Depends(deps.get_current_user)
):
    card = await service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Kontrola oprávnění
    is_admin = current_user.role == UserRole.admin
    if card.owner_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return card

# --- SOFT DELETE CARD ---
@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    service: RFIDService = Depends(get_rfid_service),
    current_user: User = Depends(deps.get_current_user)
):
    # 1. Najít kartu
    card = await service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # 2. Kontrola oprávnění (Vlastník nebo Admin)
    is_admin = current_user.role == UserRole.admin
    if card.owner_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Soft Delete
    success = await service.delete_card(card_id)
    if not success:
         # Teoreticky by se sem kód neměl dostat díky kontrole výše
         raise HTTPException(status_code=404, detail="Card not found")
    return

# --- LOOKUP (Admin Only) ---
@router.get("/lookup/{uid}", response_model=RFIDCardRead)
async def get_card_by_uid(
    uid: str,
    service: RFIDService = Depends(get_rfid_service),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role != UserRole.admin:
         raise HTTPException(status_code=403, detail="Not enough permissions")

    card = await service.get_card_by_uid(uid)
    if not card:
        raise HTTPException(status_code=404, detail="Card UID not registered")
    return card