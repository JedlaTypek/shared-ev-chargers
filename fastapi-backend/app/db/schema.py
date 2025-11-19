from typing import Optional, List
from datetime import datetime, timezone
import enum

from sqlalchemy import (
    String,
    Float,
    DateTime,
    Enum as SQLEnum,
    create_engine,
    ForeignKey,
    Numeric,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship,
)

from app.core.config import config

engine = create_engine(config.db_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


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
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

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

    charger_id: Mapped[int] = mapped_column(
        ForeignKey("chargers.id", ondelete="CASCADE"),
        nullable=False
    )

    # OCPP connector number (local to a charger)
    ocpp_number: Mapped[int] = mapped_column(nullable=False)

    type: Mapped[ConnectorType] = mapped_column(SQLEnum(ConnectorType), nullable=False)
    current_type: Mapped[CurrentType] = mapped_column(SQLEnum(CurrentType), nullable=False)
    max_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    # Foreign Key to User
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    street: Mapped[Optional[str]] = mapped_column(String(255))
    house_number: Mapped[Optional[str]] = mapped_column(String(20))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    region: Mapped[Optional[str]] = mapped_column(String(100))

    ocpp_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
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

    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    energy_kwh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[ChargeStatus] = mapped_column(
        SQLEnum(ChargeStatus),
        default=ChargeStatus.running,
        nullable=False
    )

    # Relationships (back_populates pro čitelnost a eager loading)
    user: Mapped[Optional["User"]] = relationship(back_populates="charge_logs")
    charger: Mapped[Optional["Charger"]] = relationship(back_populates="charge_logs")
    connector: Mapped[Optional["Connector"]] = relationship(back_populates="charge_logs")
    card: Mapped[Optional["RFIDCard"]] = relationship(back_populates="charge_logs")
