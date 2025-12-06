from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.schema import User
from app.models.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, session: AsyncSession):
        self._db = session

    # -------- LIST USERS --------
    async def list_users(self) -> list[User]:
        stmt = select(User)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    # -------- GET USER --------
    async def get_user(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._db.execute(stmt)
        return result.scalars().first()
    
    # -------- GET USER BY EMAIL --------
    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._db.execute(stmt)
        return result.scalars().first()

    # -------- CREATE USER --------
    async def create_user(self, user_data: UserCreate) -> User:
        # Volání async metody s await
        if await self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")

        hashed_password = user_data.password + "not_really_hashed" 
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password, 
            role=user_data.role,
            balance=user_data.balance,
        )
        
        # .add() je synchronní operace (jen přidává do session state)
        self._db.add(user)
        
        # IO operace jsou async
        await self._db.commit()
        await self._db.refresh(user)
        return user

    # -------- UPDATE USER --------
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = await self.get_user(user_id)
        if not user:
            return None

        update_fields = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_fields.items():
            if field == "password" and value:
                value = value + "not_really_hashed"
            setattr(user, field, value)

        await self._db.commit()
        await self._db.refresh(user)
        return user

    # -------- DELETE USER --------
    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        
        # .delete() je synchronní
        await self._db.delete(user)
        await self._db.commit()
        return True