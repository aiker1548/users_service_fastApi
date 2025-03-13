from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from starlette.requests import Request

from src.database.models import User
from src.users.utils import hash_password
from src.auth import verify_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/token')

async def create_user(db: AsyncSession, username: str, email: str, password: str):
    password_hash = hash_password(password)
    db_user = User(username=username, email=email, password_hash=password_hash)
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except SQLAlchemyError:
        await db.rollback()
        raise
    return db_user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result


# async def get_current_user(db: AsyncSession, token: str = Depends(oauth2_scheme)): 
#     payload = verify_access_token(token)
#     if payload is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
#     user = await get_user_by_username(db, payload.get('sub'))
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
#     return user

def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)  # Избегаем AttributeError
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

Current_user = Annotated[User, Depends(get_current_user)]