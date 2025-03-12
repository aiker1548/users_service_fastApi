from fastapi import APIRouter, status, HTTPException

from src.users.schemas import User, UserOut, UserResponseWithToken, UserToken
from src.database.core import DbSession
from src.users import crud

router = APIRouter()


@router.post("/users/", response_model=UserResponseWithToken, status_code=status.HTTP_201_CREATED)
async def register_user(db_session: DbSession, user: User):
    existing_user = await crud.get_user_by_username(db_session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    created_user = await crud.create_user(db=db_session, username=user.username, email=user.email, password=user.password_hash)
    token = created_user.create_access_token()
    return {"user": created_user, "access_token": token}

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


@router.get("/users/token/", response_model=dict, status_code=status.HTTP_200_OK)
async def get_token(db_session: DbSession, user_data: UserToken):
    user = await crud.get_user_by_username(db_session, user_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    if not user.check_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    token = user.token
    return token