from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RFIDCardBase(BaseModel):
    user_id: int
    card_uid: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class RFIDCardCreate(RFIDCardBase):
    pass


class RFIDCard(RFIDCardBase):
    id: int
    created_at: datetime
    user: Optional["User"] = None
    charge_logs: List["ChargeLog"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


if TYPE_CHECKING:
    from app.schemas.charge_log import ChargeLog
    from app.schemas.user import User


RFIDCard.model_rebuild()

