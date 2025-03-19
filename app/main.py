from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.redis_client import redis_client
from app.routes import upload, update, get_image, download, delete, token, register

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to Redis...")
    await redis_client.connect()
    yield
    print("Closing Redis connection...")
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(register.router)
app.include_router(token.router)
app.include_router(upload.router)
app.include_router(get_image.router)
app.include_router(download.router)
app.include_router(update.router)
app.include_router(delete.router)
