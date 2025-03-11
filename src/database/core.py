from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine.url import make_url
from fastapi import Depends, Request

from config import config

async def create_db_engine(connection_string: str):
    url = make_url(connection_string)
    timeout_kwargs = {
        "pool_timeout": config.DATABASE_ENGINE_POOL_TIMEOUT,
        "pool_recycle": config.DATABASE_ENGINE_POOL_RECYCLE,
        "pool_size": config.DATABASE_ENGINE_POOL_SIZE,
        "max_overflow": config.DATABASE_ENGINE_MAX_OVERFLOW,
        "pool_pre_ping": config.DATABASE_ENGINE_POOL_PING,
    }
    return create_async_engine(url, **timeout_kwargs)


#engine = create_db_engine(url=config.DATABASE_URL)
engine = create_async_engine(url=config.DATABASE_URL)

AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)


# Функция для получения сессии из request.state.db
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии БД из request.state."""
    db_session = request.state.db  # Получаем сессию из request.state
    try:
        yield db_session  # Возвращаем сессию в качестве контекста
    except Exception:
        await db_session.rollback()  # Откат при ошибке
        raise
    finally:
        # Сессия будет закрыта в middleware после запроса
        pass

DbSession = Annotated[AsyncSession, Depends(get_db)]

