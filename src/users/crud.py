from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import User
from src.users.utils import hash_password

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