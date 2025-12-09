from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ConnectorType, CurrentType

class ConnectorBase(BaseModel):
    ocpp_number: int
    
    # --- ZMĚNA: Všechna tato pole musí být Optional ---
    # Důvod: Při auto-discovery (StatusNotification) je ještě neznáme.
    type: Optional[ConnectorType] = None
    current_type: Optional[CurrentType] = None
    max_power_w: Optional[int] = None
    price_per_kwh: Optional[Decimal] = None
    # -------------------------------------------------
    
    is_active: bool = False

class ConnectorCreate(ConnectorBase):
    charger_id: int

class ConnectorUpdate(BaseModel):
    # Model pro ruční úpravu majitelem
    type: Optional[ConnectorType] = None
    current_type: Optional[CurrentType] = None
    max_power_w: Optional[int] = None
    price_per_kwh: Optional[Decimal] = None
    is_active: Optional[bool] = None

class ConnectorStatusUpdate(BaseModel):
    ocpp_id: str
    connector_number: int
    status: str
    error_code: Optional[str] = None

class ConnectorRead(ConnectorBase):
    id: int
    charger_id: int
    
    status: Optional[str] = "Unknown" 

    model_config = ConfigDict(from_attributes=True)