from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db # Import veřejné závislosti pro DB session
from app.models.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

# Dependency pro Service, která dostane DB session
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(session=db)

# -------------------- User Endpoints --------------------

@router.get("/users", response_model=list[UserRead], tags=["User"])
def get_users(service: UserService = Depends(get_user_service)):
    return service.list_users()

# Změna: Status code 201 (Created) je standard pro POST
@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["User"])
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    # Service nyní může vyhodit výjimku, pokud email existuje
    try:
        return service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}", response_model=UserRead, tags=["User"])
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserRead, tags=["User"])
def update_user(
    user_id: int, user: UserUpdate, service: UserService = Depends(get_user_service)
):
    updated = service.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/users/{user_id}", tags=["User"])
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}