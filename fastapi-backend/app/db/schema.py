from typing import Optional, List
from datetime import datetime, timezone
import enum
from decimal import Decimal

# ZMĚNA: Importy pro async SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import (
    String, Float, DateTime, Enum as SQLEnum, ForeignKey, Numeric, Integer, Boolean, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import config

# ZMĚNA: Asynchronní engine
engine = create_async_engine(config.db_url, echo=config.debug)

# ZMĚNA: Asynchronní session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


########################
# User
########################

class UserRole(enum.Enum):
    user = "user"
    owner = "owner"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.user,
        nullable=False
    )
    
    # ZMĚNA: Float -> Numeric(10, 2) pro přesné finance
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # relationships
    chargers: Mapped[List["Charger"]] = relationship(back_populates="owner")
    rfid_cards: Mapped[List["RFIDCard"]] = relationship(back_populates="owner")
    charge_logs: Mapped[List["ChargeLog"]] = relationship(back_populates="user")


########################
# RFID Cards
########################

class RFIDCard(Base):
    __tablename__ = "rfid_cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    card_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="rfid_cards")
    charge_logs: Mapped[List["ChargeLog"]] = relationship(back_populates="card")


########################
# Connectors
########################

class CurrentType(enum.Enum):
    AC = "AC"
    DC = "DC"


class ConnectorType(enum.Enum):
    Type1 = "Type1"
    Type2 = "Type2"
    CCS = "CCS"
    CHAdeMO = "CHAdeMO"
    Tesla = "Tesla"


class Connector(Base):
    __tablename__ = "connectors"

    id: Mapped[int] = mapped_column(primary_key=True)
    charger_id: Mapped[int] = mapped_column(ForeignKey("chargers.id", ondelete="CASCADE"), nullable=False)
    ocpp_number: Mapped[int] = mapped_column(nullable=False)

    # Statická data (konfigurace) - povolen NULL pro auto-discovery
    type: Mapped[Optional[ConnectorType]] = mapped_column(SQLEnum(ConnectorType), nullable=True)
    current_type: Mapped[Optional[CurrentType]] = mapped_column(SQLEnum(CurrentType), nullable=True)
    max_power_w: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_per_kwh: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    charger: Mapped["Charger"] = relationship(back_populates="connectors")
    charge_logs: Mapped[List["ChargeLog"]] = relationship(back_populates="connector")

    __table_args__ = (
        UniqueConstraint("charger_id", "ocpp_number"),
    )


########################
# Chargers
########################

class Charger(Base):
    __tablename__ = "chargers"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    street: Mapped[Optional[str]] = mapped_column(String(255))
    house_number: Mapped[Optional[str]] = mapped_column(String(20))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Unikátní identifikátor pro OCPP
    ocpp_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)

    # --- NOVÉ SLOUPCE (Metadata z BootNotification) ---
    vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # --------------------------------------------------

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="chargers")
    connectors: Mapped[List["Connector"]] = relationship(back_populates="charger")
    charge_logs: Mapped[List["ChargeLog"]] = relationship(back_populates="charger")

########################
# Charge logs
########################

class ChargeStatus(enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ChargeLog(Base):
    __tablename__ = "charge_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    charger_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chargers.id", ondelete="SET NULL"),
        nullable=True
    )

    connector_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("connectors.id", ondelete="SET NULL"),
        nullable=True
    )

    rfid_card_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rfid_cards.id", ondelete="SET NULL"),
        nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # --- PŘIDAT TOTO (chybějící sloupec pro počáteční stav elektroměru) ---
    meter_start: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # ----------------------------------------------------------------------

    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- PŘIDAT TOTO (chybějící sloupec pro konečný stav elektroměru) ---
    meter_stop: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # -------------------------------------------------------------------

    energy_wh: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    status: Mapped[ChargeStatus] = mapped_column(
        SQLEnum(ChargeStatus),
        default=ChargeStatus.running,
        nullable=False
    )

    last_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), # Automaticky se aktualizuje při každém zápisu
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="charge_logs")
    charger: Mapped[Optional["Charger"]] = relationship(back_populates="charge_logs")
    connector: Mapped[Optional["Connector"]] = relationship(back_populates="charge_logs")
    card: Mapped[Optional["RFIDCard"]] = relationship(back_populates="charge_logs")