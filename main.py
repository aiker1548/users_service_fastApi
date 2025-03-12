from fastapi import FastAPI

from src.middleware import DBSessionMiddleware  # Импортируй свою мидлвару
from src.users.views import router as user_router

app = FastAPI()

# Добавляем мидлвару в приложение
app.add_middleware(DBSessionMiddleware)

app.include_router(user_router)




