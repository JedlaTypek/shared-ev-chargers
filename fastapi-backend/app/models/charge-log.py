from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from app.models.enums import ChargeStatus


class ChargeLogBase(BaseModel):
    status: ChargeStatus # Enum (running, completed...)
    
    # ZMĚNA: Watthodiny jako Integer
    energy_wh: Optional[int] = Field(None, ge=0, description="Dodaná energie ve Wh")
    
    # ZMĚNA: Cena jako Decimal
    price: Optional[Decimal] = Field(None, ge=0)

class ChargeLogCreate(BaseModel):
    # Logy se obvykle vytváří systémově (z OCPP), ale pro admin API se to může hodit
    charger_id: int
    connector_id: int
    rfid_card_id: Optional[int] = None
    start_time: datetime = Field(default_factory=datetime.now)

class ChargeLogUpdate(BaseModel):
    # Používá se např. když dorazí "StopTransaction" z nabíječky
    end_time: Optional[datetime] = None
    energy_wh: Optional[int] = None
    price: Optional[Decimal] = None
    status: Optional[ChargeStatus] = None

class ChargeLogRead(ChargeLogBase):
    id: int
    user_id: Optional[int]
    charger_id: Optional[int]
    connector_id: Optional[int]
    rfid_card_id: Optional[int]
    
    start_time: datetime
    end_time: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)