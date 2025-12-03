from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.charger import ChargerCreate, ChargerRead, ChargerUpdate
from app.services.charger_service import ChargerService

router = APIRouter()

def get_charger_service(db: Session = Depends(get_db)) -> ChargerService:
    return ChargerService(session=db)

@router.get("", response_model=list[ChargerRead])
def get_chargers(service: ChargerService = Depends(get_charger_service)):
    return service.list_chargers()

@router.post("", response_model=ChargerRead, status_code=status.HTTP_201_CREATED)
def create_charger(
    charger_data: ChargerCreate,
    service: ChargerService = Depends(get_charger_service)
):
    try:
        return service.create_charger(charger_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{charger_id}", response_model=ChargerRead)
def get_charger(
    charger_id: int, 
    service: ChargerService = Depends(get_charger_service)
):
    charger = service.get_charger(charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger

@router.patch("/{charger_id}", response_model=ChargerRead)
def update_charger(
    charger_id: int,
    charger_update: ChargerUpdate,
    service: ChargerService = Depends(get_charger_service)
):
    updated = service.update_charger(charger_id, charger_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Charger not found")
    return updated

@router.delete("/{charger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_charger(
    charger_id: int,
    service: ChargerService = Depends(get_charger_service)
):
    success = service.delete_charger(charger_id)
    if not success:
        raise HTTPException(status_code=404, detail="Charger not found")
    return