from fastapi import FastAPI

from src.middleware import DBSessionMiddleware, AuthMiddleWare  
from src.users.views import router as user_router

app = FastAPI()

app.add_middleware(AuthMiddleWare)      #first
app.add_middleware(DBSessionMiddleware) #second

app.include_router(user_router)




