from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Charger, User
from app.schemas.charger import ChargerCreate, ChargerRead, ChargerUpdate

router = APIRouter()


@router.get("/", response_model=List[ChargerRead])
def list_chargers(db: Session = Depends(get_db)) -> List[Charger]:
    return db.query(Charger).all()


@router.post("/", response_model=ChargerRead, status_code=status.HTTP_201_CREATED)
def create_charger(payload: ChargerCreate, db: Session = Depends(get_db)) -> Charger:
    owner = db.query(User).filter(User.id == payload.owner_id).first()
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found.")

    new_charger = Charger(**payload.model_dump())
    db.add(new_charger)
    db.commit()
    db.refresh(new_charger)
    return new_charger


@router.get("/{charger_id}", response_model=ChargerRead)
def get_charger(charger_id: int, db: Session = Depends(get_db)) -> Charger:
    charger = db.query(Charger).filter(Charger.id == charger_id).first()
    if charger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Charger not found.")
    return charger


@router.patch("/{charger_id}", response_model=ChargerRead)
def update_charger(
    charger_id: int,
    payload: ChargerUpdate,
    db: Session = Depends(get_db),
) -> Charger:
    charger = db.query(Charger).filter(Charger.id == charger_id).first()
    if charger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Charger not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(charger, field, value)

    db.add(charger)
    db.commit()
    db.refresh(charger)
    return charger

