from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.connector import ConnectorRead

# --- Model pro technické údaje (z BootNotification) ---
class ChargerTechnicalStatus(BaseModel):
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

# --- MODEL PRO AUTHORIZE ---
class ChargerAuthorizeRequest(BaseModel):
    id_tag: str
# -------------------------------------

class ChargerBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    ocpp_id: Optional[str] = None
    
    # Volitelně i metadata, aby byla vidět v detailu
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

    is_active: bool = True

class ChargerCreate(ChargerBase):
    owner_id: int 

class ChargerUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None
    ocpp_id: Optional[str] = None

class ChargerRead(ChargerBase):
    id: int
    owner_id: int
    created_at: datetime
    connectors: List[ConnectorRead] = [] 

    model_config = ConfigDict(from_attributes=True)