from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class RFIDCardBase(BaseModel):
    # UID karty (hex string), min 4 znaky
    card_uid: str = Field(..., min_length=4, max_length=64)
    card_uid: str = Field(..., min_length=4, max_length=64)
    is_active: bool = True  # Soft delete
    is_enabled: bool = True # User switch

class RFIDCardCreate(RFIDCardBase):
    # ZMĚNA: Optional, protože běžný uživatel to nevyplňuje (doplní se z tokenu)
    owner_id: Optional[int] = None 

class RFIDCardUpdate(BaseModel):
    card_uid: Optional[str] = Field(None, min_length=4, max_length=64)
    card_uid: Optional[str] = Field(None, min_length=4, max_length=64)
    is_active: Optional[bool] = None  # Soft delete
    is_enabled: Optional[bool] = None # User switch

class RFIDCardRead(RFIDCardBase):
    id: int
    owner_id: int
    is_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)