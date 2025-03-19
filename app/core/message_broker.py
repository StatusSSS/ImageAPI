import aio_pika
from app.core.config import Settings


async def get_connection_and_channel():
    amqp_url = f"amqp://{Settings.RABBITMQ_USER}:{Settings.RABBITMQ_PASS}@{Settings.RABBITMQ_HOST}:5672/"
    connection = await aio_pika.connect_robust(amqp_url)
    channel = await connection.channel()
    print("Получилось присоединиться к rabbit")
    await channel.declare_queue("image_events", durable=True)
    return connection, channel

async def send_message(event_type, image_id):
    connection, channel =await get_connection_and_channel()
    message = f"{event_type}: Image ID: {image_id}"
    await channel.default_exchange.publish(
        aio_pika.Message(body=message.encode()),
        routing_key="image_events",
    )

    print(f" [X] Sent '{message}' ")
    await channel.close()
    await connection.close()