from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.schema import User
from app.models.user import UserCreate, UserUpdate

# Pro hashování hesel (zatím jen placeholder, později použij passlib)
# from passlib.context import CryptContext 
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, session: Session):
        self._db = session

    # -------- LIST USERS --------
    def list_users(self) -> list[User]:
        # Moderní syntaxe SQLAlchemy 2.0
        stmt = select(User)
        result = self._db.execute(stmt)
        return result.scalars().all()

    # -------- GET USER --------
    def get_user(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self._db.execute(stmt).scalars().first()
    
    # -------- GET USER BY EMAIL (pomocná funkce) --------
    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.execute(stmt).scalars().first()

    # -------- CREATE USER --------
    def create_user(self, user_data: UserCreate) -> User:
        # 1. Kontrola duplicity emailu (čistší než chytat IntegrityError)
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")

        # 2. Hashování hesla (TODO: Implementovat doopravdy)
        hashed_password = user_data.password + "not_really_hashed" 
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password, 
            role=user_data.role,
            balance=user_data.balance,
        )
        
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    # -------- UPDATE USER --------
    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = self.get_user(user_id)
        if not user:
            return None

        update_fields = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_fields.items():
            # Pokud se mění heslo, musíme ho znovu zahashovat!
            if field == "password" and value:
                value = value + "not_really_hashed" # TODO: Hash
            
            setattr(user, field, value)

        self._db.commit()
        self._db.refresh(user)
        return user

    # -------- DELETE USER --------
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        self._db.delete(user)
        self._db.commit()
        return True