from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ConnectorBase(BaseModel):
    charger_id: int
    connector_type_id: int
    connector_number: int
    max_power_kw: Decimal
    price_per_kwh: Decimal
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ConnectorCreate(ConnectorBase):
    pass


class Connector(ConnectorBase):
    id: int
    charger: Optional["Charger"] = None
    type: Optional["ConnectorType"] = None
    charge_logs: List["ChargeLog"] = Field(default_factory=list)
    reservations: List["Reservation"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


if TYPE_CHECKING:
    from app.schemas.charge_log import ChargeLog
    from app.schemas.charger import Charger
    from app.schemas.connector_type import ConnectorType
    from app.schemas.reservation import Reservation


Connector.model_rebuild()

