from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ConfigDict

from app.models.reservation import ReservationStatus


class ReservationBase(BaseModel):
    user_id: int
    charger_id: int
    connector_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    status: ReservationStatus = ReservationStatus.active

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: int
    user: Optional["User"] = None
    charger: Optional["Charger"] = None
    connector: Optional["Connector"] = None

    model_config = ConfigDict(from_attributes=True)


if TYPE_CHECKING:
    from app.schemas.charger import Charger
    from app.schemas.connector import Connector
    from app.schemas.user import User


Reservation.model_rebuild()

