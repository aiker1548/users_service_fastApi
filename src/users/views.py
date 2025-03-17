from fastapi import APIRouter, status, HTTPException, Depends

from src.users.schemas import User, UserOut, UserResponseWithToken, UserToken, UserIdsRequest
from src.database.core import DbSession
from src.users.crud import Current_user, get_user_by_username, get_users as get_users_service, create_user
from src.users.crud import get_users_by_ids
router = APIRouter()


@router.post("/users/", response_model=UserResponseWithToken, status_code=status.HTTP_201_CREATED)
async def register_user(db_session: DbSession, user: User):
    existing_user = await get_user_by_username(db_session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    created_user = await create_user(db=db_session, username=user.username, email=user.email, password=user.password)
    token = created_user.token
    return {"user": created_user, "access_token": token}

@router.get("/users/{username}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user_by_name(db_session: DbSession, username: str):
    user = await get_user_by_username(db_session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    return user
    
@router.get("/users/", response_model=list[UserOut], status_code=status.HTTP_200_OK)
async def get_users(db_session: DbSession):
    users = await get_users_service(db_session)
    return users.scalars().all()


@router.post("/users/token/", response_model=dict, status_code=status.HTTP_200_OK)
async def get_token(db_session: DbSession, user_data: UserToken):
    user = await get_user_by_username(db_session, user_data.username)
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

@router.get('/users/me/', response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(user: Current_user):
    return user


@router.post('/users/batch/', response_model=list[UserOut], status_code=status.HTTP_200_OK)
async def get_batch_users(db_session: DbSession, request: UserIdsRequest):
    users = await get_users_by_ids(db_session, request.user_ids)
    return users