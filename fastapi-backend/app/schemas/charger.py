from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChargerBase(BaseModel):
    owner_id: int
    name: str
    latitude: Decimal
    longitude: Decimal
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    ocpp_id: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ChargerCreate(ChargerBase):
    pass


class ChargerUpdate(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region: Optional[str] = None
    ocpp_id: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class Charger(ChargerBase):
    id: int
    created_at: datetime
    owner: Optional["User"] = None
    connectors: List["Connector"] = Field(default_factory=list)
    charge_logs: List["ChargeLog"] = Field(default_factory=list)
    reservations: List["Reservation"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Backwards compatibility
ChargerRead = Charger


if TYPE_CHECKING:
    from app.schemas.charge_log import ChargeLog
    from app.schemas.connector import Connector
    from app.schemas.reservation import Reservation
    from app.schemas.user import User


Charger.model_rebuild()