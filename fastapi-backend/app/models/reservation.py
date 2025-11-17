from enum import Enum
from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import relationship

from app.database import Base


class ReservationStatus(str, Enum):
    active = "active"
    cancelled = "cancelled"
    completed = "completed"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    charger_id = Column(Integer, ForeignKey("chargers.id", ondelete="CASCADE"), nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id", ondelete="SET NULL"))
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    status = Column(PgEnum(ReservationStatus), default=ReservationStatus.active)

    user = relationship("User", back_populates="reservations")
    charger = relationship("Charger", back_populates="reservations")
    connector = relationship("Connector", back_populates="reservations")
