from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ConfigDict

from app.models.charge_log import ChargeStatus


class ChargeLogBase(BaseModel):
    user_id: Optional[int] = None
    charger_id: Optional[int] = None
    connector_id: Optional[int] = None
    rfid_card_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_kwh: Optional[Decimal] = None
    price: Optional[Decimal] = None
    status: ChargeStatus = ChargeStatus.running

    model_config = ConfigDict(from_attributes=True)


class ChargeLogCreate(ChargeLogBase):
    charger_id: int
    connector_id: int


class ChargeLogUpdate(BaseModel):
    user_id: Optional[int] = None
    charger_id: Optional[int] = None
    connector_id: Optional[int] = None
    rfid_card_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    energy_kwh: Optional[Decimal] = None
    price: Optional[Decimal] = None
    status: Optional[ChargeStatus] = None

    model_config = ConfigDict(from_attributes=True)


class ChargeLog(ChargeLogBase):
    id: int
    user: Optional["User"] = None
    charger: Optional["Charger"] = None
    connector: Optional["Connector"] = None
    rfid_card: Optional["RFIDCard"] = None

    model_config = ConfigDict(from_attributes=True)


# Backwards compatibility
ChargeLogRead = ChargeLog


if TYPE_CHECKING:
    from app.schemas.charger import Charger
    from app.schemas.connector import Connector
    from app.schemas.rfid import RFIDCard
    from app.schemas.user import User


ChargeLog.model_rebuild()