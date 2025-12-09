from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ConnectorType, CurrentType

class ConnectorBase(BaseModel):
    ocpp_number: int
    
    type: Optional[ConnectorType] = None
    current_type: Optional[CurrentType] = None
    max_power_w: Optional[int] = None
    price_per_kwh: Optional[Decimal] = None
    
    is_active: bool = False

class ConnectorCreate(ConnectorBase):
    charger_id: int

# Model pro PATCH requesty (úprava majitelem)
class ConnectorUpdate(BaseModel):
    type: Optional[ConnectorType] = None
    current_type: Optional[CurrentType] = None
    max_power_w: Optional[int] = None
    price_per_kwh: Optional[Decimal] = None
    is_active: Optional[bool] = None

# Model pro data z OCPP serveru
class ConnectorStatusUpdate(BaseModel):
    ocpp_id: str
    connector_number: int
    status: str
    error_code: Optional[str] = None

class ConnectorRead(ConnectorBase):
    id: int
    charger_id: int
    
    # Status se dolepí z Redisu, v DB není
    status: Optional[str] = "Unknown"

    model_config = ConfigDict(from_attributes=True)