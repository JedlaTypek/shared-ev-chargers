from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ConnectorType, CurrentType

class ConnectorBase(BaseModel):
    ocpp_number: int
    type: ConnectorType
    current_type: CurrentType
    max_power_w: int
    price_per_kwh: Decimal
    is_active: bool = True

class ConnectorCreate(ConnectorBase):
    charger_id: int

class ConnectorUpdate(BaseModel):
    type: Optional[ConnectorType] = None
    max_power_w: Optional[int] = None
    price_per_kwh: Optional[Decimal] = None
    is_active: Optional[bool] = None

class ConnectorRead(ConnectorBase):
    id: int
    charger_id: int
    
    model_config = ConfigDict(from_attributes=True)