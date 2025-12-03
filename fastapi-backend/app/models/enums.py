from enum import Enum

# Enum pro uživatelské role
class UserRole(str, Enum):
    user = "user"
    owner = "owner"
    admin = "admin"

class CurrentType(str, Enum):
    AC = "AC"
    DC = "DC"

class ConnectorType(str, Enum):
    Type1 = "Type1"
    Type2 = "Type2"
    CCS = "CCS"
    CHAdeMO = "CHAdeMO"
    Tesla = "Tesla"

class ChargeStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"