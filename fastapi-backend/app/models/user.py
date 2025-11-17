from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum pro uživatelské role
class UserRole(str, Enum):
    user = "user"
    owner = "owner"
    admin = "admin"

# Model pro vytváření uživatele
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.user
    balance: Optional[float] = 0.0

# Model pro čtení uživatele
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    balance: float
    created_at: datetime

    class Config:
        orm_mode = True

# Model pro aktualizaci uživatele
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    balance: Optional[float] = None