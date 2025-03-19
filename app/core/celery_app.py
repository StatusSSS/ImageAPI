from celery import Celery
import os
from dotenv import load_dotenv


load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD")

broker_url = f"pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}//"

celery_app = Celery(
    "tasks",
    broker=broker_url,
    backend="rpc://"
)

from app.services import task
