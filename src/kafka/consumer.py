import json
import time

from aiokafka import AIOKafkaConsumer
from fastapi.encoders import jsonable_encoder

from src.database.core import AsyncSessionMaker
from src.users.crud import get_users_by_ids
from config import config as kafka_config
from src.kafka.producer import send_users_to_topic


async def consume_kafka_messages():
    """Слушает запросы на получение пользователей (BAT запрос)"""
    consumer = AIOKafkaConsumer(
        kafka_config.request_topic,  
        bootstrap_servers=kafka_config.bootstrap_servers,
        group_id=kafka_config.group_id,
        auto_offset_reset="earliest"
    )
    await consumer.start()

    try:
        async for msg in consumer:
            try:
                request_data = json.loads(msg.value.decode("utf-8"))
                correlation_id = request_data.get("correlation_id")  # Получаем correlation_id из запроса
                user_ids = request_data.get("user_ids")  # Получаем список ID пользователей
                if not user_ids:
                    continue  # Если ID пользователей нет, пропускаем
                
                async with AsyncSessionMaker() as session:
                    # Получаем пользователей по ID
                    start = time.time()
                    users = await get_users_by_ids(session, user_ids)
                    users_data = {user.id: jsonable_encoder(user) for user in users}  # Создаем мап id → json
                    # Отправляем результат обратно в Kafka с тем же correlation_id
                    response_data = {
                        "correlation_id": correlation_id,
                        "users": users_data
                    }

                    # Отправляем данные в response_topic
                    await send_users_to_topic(response_data)
                    print(f"Kafka time: {time.time() - start:.3f} sec")
            except Exception as e:
                print(e)

    finally:
        await consumer.stop()

