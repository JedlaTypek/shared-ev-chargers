from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schema import User
from app.models.user import UserCreate, UserUpdate
from app.core.config import config
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, session: AsyncSession):
        self._db = session

    async def list_users(self, show_all: bool = False) -> list[User]:
        stmt = select(User)
        
        # Pokud nechceme vidět všechny (i smazané), vyfiltrujeme jen aktivní
        if not show_all:
            stmt = stmt.where(User.is_active == True) # noqa: E712
            
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_user(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user_data: UserCreate) -> User:
        if await self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")

        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password, 
            role=user_data.role,
            balance=user_data.balance,
        )
        
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    # -------- UPDATE USER --------
    async def update_user(self, user_id: int, user_data: UserUpdate, verify_old_password: bool = True) -> User | None:
        user = await self.get_user(user_id)
        if not user:
            return None

        # Pydantic metoda .model_dump(exclude_unset=True) vrátí jen to, co uživatel poslal
        update_fields = user_data.model_dump(exclude_unset=True)
        
        # Ošetření změny hesla
        if "password" in update_fields:
            new_password = update_fields["password"]
            
            # Pokud se mění heslo a je vyžadováno ověření původního
            if verify_old_password:
                old_password = update_fields.get("old_password")
                if not old_password:
                     raise ValueError("Old password is required to change password")
                
                if not verify_password(old_password, user.password):
                     raise ValueError("Incorrect old password")
            
            # Zahashujeme nové heslo
            update_fields["password"] = get_password_hash(new_password)
            
        # Odstraníme 'old_password' z polí k update (není v DB modelu)
        update_fields.pop("old_password", None)
        
        for field, value in update_fields.items():
            setattr(user, field, value)

        await self._db.commit()
        await self._db.refresh(user)
        return user

    # -------- DELETE USER --------
    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.is_active = False  # Soft delete
        await self._db.commit()
        return True