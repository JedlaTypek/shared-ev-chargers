from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class RFIDCardBase(BaseModel):
    # UID karty (hex string), min 4 znaky
    card_uid: str = Field(..., min_length=4, max_length=64)
    is_active: bool = True

class RFIDCardCreate(RFIDCardBase):
    # TODO: Až bude login, toto pole zmizí a vezme se z tokenu
    owner_id: int

class RFIDCardUpdate(BaseModel):
    card_uid: Optional[str] = Field(None, min_length=4, max_length=64)
    is_active: Optional[bool] = None

class RFIDCardRead(RFIDCardBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)