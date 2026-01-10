from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.connector import ConnectorRead

class ChargerTechnicalStatus(BaseModel):
    """
    Tento model slouží pouze pro backend/OCPP logiku.
    Uživatel ho nevyplňuje ručně.
    """
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

class ChargerAuthorizeRequest(BaseModel):
    id_tag: str

class ChargerExistenceCheck(BaseModel):
    id: int
    is_active: bool

class ChargerBase(BaseModel):
    """
    Základní pole, která může běžný uživatel ovlivnit.
    ZDE UŽ NEJSOU TECHNICKÁ DATA (vendor, model, atd.)
    """
    name: str
    latitude: float
    longitude: float
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    region: Optional[str] = None
    is_active: bool = True     # Soft delete
    is_enabled: bool = True    # User switch (default True on creation)

class ChargerCreate(ChargerBase):
    """
    Model pro vytváření nabíječky uživatelem.
    """
    owner_id: Optional[int] = None
    # ocpp_id je generováno systémem, uživatel ho nesmí zadávat
    # Technická data (vendor, model, serial_number, firmware_version) se doplní sama až po prvním připojení.

class ChargerUpdate(BaseModel):
    """
    Model pro editaci uživatelem.
    Obsahuje jen to, co smí uživatel změnit (název, adresa, poloha).
    """
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None  # Soft delete restore/archive
    is_enabled: Optional[bool] = None # User switch
    
    # Zde záměrně CHYBÍ vendor, model, serial_number, ocpp_id.
    # Uživatel je nemůže přes API změnit.

class ChargerRead(ChargerBase):
    """
    Model pro čtení (odpověď API).
    Zde vracíme i technická data, aby je uživatel viděl,
    i když je nemůže editovat.
    """
    id: int
    ocpp_id: str
    owner_id: int
    is_enabled: bool # Make sure it's explicit in Read model (inherited from Base but good to double check)
    created_at: datetime

    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

    connectors: List[ConnectorRead] = [] 

    model_config = ConfigDict(from_attributes=True)