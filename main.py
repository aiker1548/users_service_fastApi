from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middleware import DBSessionMiddleware, AuthMiddleWare  
from src.users.views import router as user_router
from src.kafka.consumer import consume_kafka_messages  # Функция для обработки Kafka


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запускаем консьюмера перед запуском FastAPI и закрываем его при завершении."""
    task = asyncio.create_task(consume_kafka_messages())  
    try:
        yield
    finally:
        task.cancel()  
        try:
            await task  
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthMiddleWare)      
app.add_middleware(DBSessionMiddleware)

origins = ["http://localhost:3000", "http://127.0.0.1:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
