from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base


class RFIDCard(Base):
    __tablename__ = "rfid_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_uid = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="rfid_cards")
    charge_logs = relationship("ChargeLog", back_populates="rfid_card")
