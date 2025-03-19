from fastapi import APIRouter, UploadFile, File, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import  get_db
from ..db.models import Image, User

from app.core.message_broker import send_message
import asyncio
import aiofiles
import os
from datetime import datetime
from pathlib import Path

from app.services.auth import get_current_user
from app.core.redis_client import redis_client
import json



router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    dependencies=[Depends(get_current_user)]
)

UPLOAD_DIR = Path("./app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



@router.post("")
async def upload_file(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    file_path = UPLOAD_DIR / file.filename
    print(file_path)
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    size = await asyncio.to_thread(os.path.getsize, file_path)

    new_image = Image(
        user_id=user.id,
        name=file.filename,
        file_path=str(file_path),
        download_date=datetime.utcnow(),
        resolution=0,
        size=size
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)

    image_data = {
        "user_id": new_image.user_id,
        "name": new_image.name,
        "file_path": new_image.file_path,
        "tags": new_image.tags,
    }

    cache_key = f"image_data: {new_image.id}"

    await redis_client.set(cache_key, json.dumps(image_data), 3600)

    await send_message("upload", new_image.id)

    return {
        "detail": "image uploaded",
        "image_id": new_image.id,
    }
