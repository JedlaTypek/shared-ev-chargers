from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Numeric, TIMESTAMP, Enum as PgEnum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class UserRole(str, Enum):
    user = "user"
    owner = "owner"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255))
    role = Column(PgEnum(UserRole), default=UserRole.user, nullable=False)
    balance = Column(Numeric(10, 2), default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    chargers = relationship("Charger", back_populates="owner", cascade="all, delete")
    rfid_cards = relationship("RFIDCard", back_populates="user", cascade="all, delete")
    charge_logs = relationship("ChargeLog", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
