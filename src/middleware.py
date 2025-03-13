from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request

from src.database.core import AsyncSessionMaker
from src.auth import verify_access_token
from src.users.crud import get_user_by_username

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерация уникального ID запроса

        # Создаем сессию для этого запроса и прокидываем её в request.state.db
        async with AsyncSessionMaker() as session:
            request.state.db = session  # Прокидываем сессию
            response = await call_next(request)  # Обрабатываем запрос
            await session.close()  # Закрываем сессию после запроса

        return response
    

class AuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer'):
            token = token.split("Bearer ")[-1].strip()
            payload = verify_access_token(token)
            request.state.username = payload.get("sub")
            
        return await call_next(request)
                
        