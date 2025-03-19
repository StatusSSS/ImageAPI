from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.auth import get_current_user
from ..db.database import  get_db
from ..db.models import Image, User, ChangedImages

from app.core.message_broker import send_message

import os
from app.core.redis_client import redis_client
from pathlib import Path




router = APIRouter(
    prefix="/delete/{image_id}",
    tags=["delete image"],
    dependencies=[Depends(get_current_user)]
)


UPLOAD_DIR = Path("./app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.delete("")
async def delete_image(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    get_image_db = await db.execute(select(Image).where(Image.id == image_id))
    image_db = get_image_db.scalar()

    if not image_db:
        raise HTTPException(
            status_code=404,
            detail="image not found"
        )

    if image_db.user_id == user.id:

        cache_image_key = f"image_data: {image_id}"
        cache_changed_key = f"changed_data: {image_id}"

        try:
            redis_client.delete(cache_image_key)
            redis_client.delete(cache_changed_key)
        except Exception as e:
            print(e)

        get_changed_db = await db.execute(select(ChangedImages).where(ChangedImages.image_id == image_id))
        changed_db = get_changed_db.scalar()


        if os.path.exists(changed_db.resized_file_path):
            os.remove(changed_db.resized_file_path)
            os.remove(changed_db.grey_file_path)

        if os.path.exists(image_db.file_path):
            os.remove(image_db.file_path)

        await db.delete(image_db)
        await db.commit()

        await send_message("delete", image_db.id)

        return {
            "detail": "image deleted",
        }

    return {
        "detail": "you don't have permission to delete this image"
    }