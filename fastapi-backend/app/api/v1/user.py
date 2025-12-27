from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1 import deps  # Import deps
from app.api.v1.deps import get_db, get_current_user # Import get_current_user
from app.models.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from app.db.schema import User # Potřebujeme pro typovou kontrolu
from app.models.enums import UserRole # Potřebujeme pro kontrolu role

router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session=db)

# --- GET ALL USERS (Jen pro Adminy?) ---
@router.get("/", response_model=list[UserRead])
async def get_users(
    show_all: bool = False, # ?show_all=true zobrazí i smazané
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    # Předáme parametr do service
    return await service.list_users(show_all=show_all)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
    # Použijeme get_current_user_optional (viz bod 2 níže, pokud ho ještě nemáš)
    current_user: User | None = Depends(deps.get_current_user_optional)
):
    try:
        # Zjistíme, jestli akci provádí Admin
        is_admin = current_user and current_user.role == UserRole.admin

        # POKUD TO NENÍ ADMIN (tzn. běžná registrace nebo hacker)
        if not is_admin:
            # 1. Bezpečnostní pojistka: Nikdo se nesmí sám registrovat jako Admin
            if user_data.role == UserRole.admin:
                raise HTTPException(
                    status_code=403, 
                    detail="Cannot register as Admin. Please contact support."
                )
            
            # 2. Povolíme roli 'owner' nebo 'user'.
            # Pokud uživatel nic nepošle (je to None), nastavíme default 'user'.
            if not user_data.role:
                user_data.role = UserRole.user
            
            # 3. Vynutíme ostatní bezpečné hodnoty
            user_data.balance = 0
            user_data.is_active = True 

        # Pokud je to Admin, necháme projít všechno (může vytvářet adminy i měnit zůstatky)
        
        return await service.create_user(user_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Vrátí data aktuálně přihlášeného uživatele.
    Frontend toto volá hned po přihlášení, aby zjistil jméno, roli a zůstatek.
    """
    return current_user

# --- GET USER BY ID ---
@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int, 
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    # Kontrola: Admin může vidět kohokoliv, uživatel jen sebe
    is_admin = current_user.role == UserRole.admin # Nebo current_user.is_superuser
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- UPDATE USER ---
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role == UserRole.admin

    # 1. Kontrola oprávnění (Admin nebo vlastník)
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 2. Bezpečnostní pojistka: Běžný uživatel nesmí měnit svou roli ani zůstatek!
    if not is_admin:
        if user_data.role is not None:
             raise HTTPException(status_code=403, detail="Cannot change own role")
        if user_data.balance is not None:
             raise HTTPException(status_code=403, detail="Cannot change own balance manually")

    updated = await service.update_user(user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

# --- DELETE USER ---
@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role == UserRole.admin

    # Kontrola: Admin nebo vlastník
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}