from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as PgEnum
from sqlalchemy.orm import relationship
from .user import Base


class CurrentType(str, Enum):
    AC = "AC"
    DC = "DC"


class ConnectorType(Base):
    __tablename__ = "connector_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    current_type = Column(PgEnum(CurrentType), nullable=False)

    connectors = relationship("Connector", back_populates="type")
