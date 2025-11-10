from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import relationship
from .user import Base


class ChargeStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ChargeLog(Base):
    __tablename__ = "charge_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    charger_id = Column(Integer, ForeignKey("chargers.id", ondelete="SET NULL"))
    connector_id = Column(Integer, ForeignKey("connectors.id", ondelete="SET NULL"))
    rfid_card_id = Column(Integer, ForeignKey("rfid_cards.id", ondelete="SET NULL"))
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    energy_kwh = Column(Numeric(8, 3))
    price = Column(Numeric(7, 2))
    status = Column(PgEnum(ChargeStatus), default=ChargeStatus.running)

    user = relationship("User", back_populates="charge_logs")
    charger = relationship("Charger", back_populates="charge_logs")
    connector = relationship("Connector", back_populates="charge_logs")
    rfid_card = relationship("RFIDCard", back_populates="charge_logs")
