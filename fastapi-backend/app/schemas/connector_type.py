from typing import TYPE_CHECKING, List

from pydantic import BaseModel, ConfigDict, Field

from app.models.connector_type import CurrentType


class ConnectorTypeBase(BaseModel):
    name: str
    current_type: CurrentType

    model_config = ConfigDict(from_attributes=True)


class ConnectorTypeCreate(ConnectorTypeBase):
    pass


class ConnectorType(ConnectorTypeBase):
    id: int
    connectors: List["Connector"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


if TYPE_CHECKING:
    from app.schemas.connector import Connector


ConnectorType.model_rebuild()

