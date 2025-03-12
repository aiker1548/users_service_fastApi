from fastapi import APIRouter, status, HTTPException

from src.users.schemas import UserCreate, UserOut
from src.database.core import DbSession
from src.users import crud

router = APIRouter()


@router.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(db_session: DbSession, user: UserCreate):
    existing_user = await crud.get_user_by_username(db_session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    created_user = await crud.create_user(db=db_session, username=user.username, email=user.email, password=user.password_hash)
    return created_user

@router.get("/users/{username}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user_by_name(db_session: DbSession, username: str):
    user = await crud.get_user_by_username(db_session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    return user
    
@router.get("/users/", response_model=list[UserOut], status_code=status.HTTP_200_OK)
async def get_users(db_session: DbSession):
    users = await crud.get_users(db_session)
    return users.scalars().all()