import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from config import config as kafka_config

async def send_users_to_topic(users_data):
    """Отправляет список пользователей обратно в Kafka"""
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_config.bootstrap_servers
    )
    await producer.start()
    try:
        await producer.send_and_wait(
            kafka_config.response_topic,  
            json.dumps(users_data).encode("utf-8")  # Отправляем JSON со всеми пользователями
        )
    finally:
        await producer.stop()

