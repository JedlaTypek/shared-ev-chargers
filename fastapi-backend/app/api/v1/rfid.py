from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.models.rfid import RFIDCardCreate, RFIDCardRead, RFIDCardUpdate
from app.services.rfid_service import RFIDService

router = APIRouter()

def get_rfid_service(db: AsyncSession = Depends(get_db)) -> RFIDService:
    return RFIDService(session=db)

@router.get("", response_model=list[RFIDCardRead])
async def get_cards(service: RFIDService = Depends(get_rfid_service)):
    return await service.list_cards()

@router.post("", response_model=RFIDCardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: RFIDCardCreate,
    service: RFIDService = Depends(get_rfid_service)
):
    try:
        return await service.create_card(card_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{card_id}", response_model=RFIDCardRead)
async def get_card(
    card_id: int, 
    service: RFIDService = Depends(get_rfid_service)
):
    card = await service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.get("/lookup/{uid}", response_model=RFIDCardRead)
async def get_card_by_uid(
    uid: str,
    service: RFIDService = Depends(get_rfid_service)
):
    card = await service.get_card_by_uid(uid)
    if not card:
        raise HTTPException(status_code=404, detail="Card UID not registered")
    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    service: RFIDService = Depends(get_rfid_service)
):
    success = await service.delete_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return