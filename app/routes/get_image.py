from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.database import  get_db
from ..db.models import Image, User
from app.services.auth import get_current_user
from app.core.redis_client import redis_client

from pathlib import Path
import json


router = APIRouter(
    prefix="/images/{image_id}",
    tags=["get image"],
    dependencies=[Depends(get_current_user)]
)

UPLOAD_DIR = Path("./app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)



@router.get("")
async def get_image(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    get_image_db = await db.execute(select(Image).where(Image.id == image_id))
    image_db = get_image_db.scalar()

    if not image_db:
        raise HTTPException(
            status_code=404,
            detail="image not found"
        )

    if image_db.user_id == user.id:
        cache_key = f"image_data: {image_id}"
        cache_data = await redis_client.get(cache_key)

        if cache_data:
            dict_cache_data = json.loads(cache_data)
            return_data = {
                "user_id": dict_cache_data["user_id"],
                "name": dict_cache_data["name"],
                "file_path": dict_cache_data["file_path"],
                "tags": dict_cache_data["tags"],
            }
        else:
            cache_data = None

        if cache_data is None:
            image_db = await db.execute(select(Image).where(Image.id == image_id))
            image = image_db.scalar()
            return_data = {
                "name": image.name,
                "file_path": image.file_path,
                "tags": image.tags,
            }

            if not return_data:
                return HTTPException(
                    status_code=404,
                    detail="image not found",
                )

        return {
            "image_id": image_id,
            "name": return_data["name"],
            "file_path": return_data["file_path"],
            "tags": return_data["tags"],
        }

    return {
        "detail": "you don't have permission to get this image"
    }