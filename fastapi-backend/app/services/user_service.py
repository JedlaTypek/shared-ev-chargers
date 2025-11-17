from sqlalchemy.orm import Session
from app.db.schema import User
from app.models.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: Session):
        self._db = session

    # -------- LIST USERS --------
    def list_users(self) -> list[User]:
        return self._db.query(User).all()

    # -------- GET USER --------
    def get_user(self, user_id: int) -> User | None:
        return self._db.query(User).filter(User.id == user_id).first()

    # -------- CREATE USER --------
    def create_user(self, user_data: UserCreate) -> User:
        # vytvoříme ORM objekt User (SQLAlchemy model)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,   # tady budeš později hashovat
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

        # projdi jednotlivá pole a jen ta, která nejsou None, aktualizuj
        update_fields = user_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
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
