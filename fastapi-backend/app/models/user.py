from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole

# Model pro vytváření uživatele
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.user
    
    # Změna na Decimal. Výchozí hodnota jako string "0.00" zajistí přesnost.
    balance: Optional[Decimal] = Decimal("0.00")

# Model pro čtení uživatele (Response)
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    
    # Změna na Decimal
    balance: Decimal
    
    created_at: datetime

    # Moderní konfigurace pro Pydantic V2 (nahrazuje class Config)
    model_config = ConfigDict(from_attributes=True)

# Model pro aktualizaci uživatele
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    
    # Změna na Decimal
    balance: Optional[Decimal] = None