from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as PgEnum
from sqlalchemy.orm import relationship
from app.database import Base


class CurrentType(str, Enum):
    AC = "AC"
    DC = "DC"


class ConnectorType(Base):
    __tablename__ = "connector_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    current_type = Column(PgEnum(CurrentType), nullable=False)

    # Vztah k tabulce connectors (každý typ může mít více konektorů)
    connectors = relationship("Connector", back_populates="type")
