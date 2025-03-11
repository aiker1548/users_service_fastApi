from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User
from src.users.schemas import UserCreate

async def create_user(db: AsyncSession, username: str, email: str, password: str):
    db_user = User(username=username, email=email, password_hash=password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result