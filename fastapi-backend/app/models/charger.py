from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base


class Charger(Base):
    __tablename__ = "chargers"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    street = Column(String(255))
    house_number = Column(String(20))
    city = Column(String(100))
    postal_code = Column(String(20))
    region = Column(String(100))
    ocpp_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    owner = relationship("User", back_populates="chargers")
    connectors = relationship("Connector", back_populates="charger", cascade="all, delete")
    charge_logs = relationship("ChargeLog", back_populates="charger")
    reservations = relationship("Reservation", back_populates="charger")
