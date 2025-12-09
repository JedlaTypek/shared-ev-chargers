from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.connector import ConnectorRead

# 1. BASE: Jen to, co je bezpečné a společné pro všechny
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
    is_active: bool = True

# 2. CREATE: Co zadává uživatel při registraci (Base + owner_id)
class ChargerCreate(ChargerBase):
    owner_id: int 

# 3. UPDATE: Co může uživatel měnit ručně
class ChargerUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None
    ocpp_id: Optional[str] = None

# 4. TECHNICAL STATUS: Specializovaný model pro "System Update" (z BootNotification)
# Toto NENÍ v Base, protože to uživatel nikdy nezadává ručně.
class ChargerTechnicalStatus(BaseModel):
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

# 5. READ (Public): Verze pro mapu a běžné uživatele
class ChargerRead(ChargerBase):
    id: int
    created_at: datetime
    # Pro veřejnost stačí vědět, co to je za konektory, ale ne verzi FW
    connectors: List[ConnectorRead] = []
    
    # Zde můžeme přidat Vendor/Model (to je dobré pro marketing),
    # ale vynechat SerialNumber a Firmware (to je interní).
    vendor: Optional[str] = None
    model: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# 6. READ (Owner/Admin): Plná verze s detaily
# Dědí z ChargerRead a PŘIDÁVÁ citlivé technické údaje
class ChargerOwnerRead(ChargerRead):
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None

class ChargerAuthorizeRequest(BaseModel):
    id_tag: str