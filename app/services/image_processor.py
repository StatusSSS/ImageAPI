import asyncio

import aio_pika
from aio_pika import IncomingMessage

from app.core.config import settings
from app.services.task import process_image
import time
import sys


sys.stdout.reconfigure(line_buffering=True)


async def connect_to_rabbitmq():
    retries = 5
    while retries > 0:
        try:
            amqp_url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"
            connection = await aio_pika.connect_robust(url=amqp_url)
            print("Подключено к RabbitMQ")
            return connection
        except Exception as e:
            print(f"  Не удалось подключиться, пробую снова... ({6 - retries}/5)")
            retries -= 1
            time.sleep(5)

    raise Exception(" Не удалось подключиться к RabbitMQ после 5 попыток")

async def handle_message(message: IncomingMessage):
    async with message.process():
        body = message.body.decode()
        print(f" [X] Получил {body}")

        if "upload" in body.lower():
            try:
                image_id_str = body.split(":")[-1].strip()
                image_id = int(image_id_str)
                process_image.delay(image_id)
            except ValueError:
                print("Не удалось распарсить ImageID")


async def listen_for_events():
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()

    queue = await channel.declare_queue("image_events", durable=True)

    print(" [X] Waiting for messages. To exit press CTRL+C")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await handle_message(message)

    await channel.close()
    await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(listen_for_events())
    except KeyboardInterrupt:
        print("Остановлено")