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

class ConnectorStatusUpdate(BaseModel):
    ocpp_id: str
    connector_number: int
    status: str
    error_code: Optional[str] = None

class ConnectorRead(ConnectorBase):
    id: int
    charger_id: int
    
    # Toto pole vyplníme z Redisu, v PostgreSQL není
    status: Optional[str] = "Unknown" 

    model_config = ConfigDict(from_attributes=True)