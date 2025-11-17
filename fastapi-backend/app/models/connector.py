from sqlalchemy import Column, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    charger_id = Column(Integer, ForeignKey("chargers.id", ondelete="CASCADE"), nullable=False)
    connector_type_id = Column(Integer, ForeignKey("connector_types.id", ondelete="RESTRICT"), nullable=False)
    connector_number = Column(Integer, nullable=False)
    max_power_kw = Column(Numeric(5, 2), nullable=False)
    price_per_kwh = Column(Numeric(5, 2), nullable=False)
    is_active = Column(Boolean, default=True)

    charger = relationship("Charger", back_populates="connectors")
    type = relationship("ConnectorType", back_populates="connectors")
    charge_logs = relationship("ChargeLog", back_populates="connector")
    reservations = relationship("Reservation", back_populates="connector")
