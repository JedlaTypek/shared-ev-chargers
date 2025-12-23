from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db
from app.models.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session=db)

# ZMĚNA: Cesta je jen "/", protože prefix "/users" už je v main.py
# ZMĚNA: Odstraněno tags=["User"], protože tag se dědí z main.py
@router.get("/", response_model=list[UserRead])
async def get_users(service: UserService = Depends(get_user_service)):
    return await service.list_users()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return await service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ZMĚNA: Cesta zkrácena na "/{user_id}"
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, user: UserUpdate, service: UserService = Depends(get_user_service)
):
    updated = await service.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}