from fastapi import APIRouter, HTTPException, Depends


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
from ..db.database import  get_db
from ..db.models import Image, User

from app.core.redis_client import redis_client
from app.services.auth import get_current_user
from pathlib import Path
from app.schemas.image_schema import ImageUpdate


router = APIRouter(
    prefix="/images/update/{image_id}",
    tags=["update image"],
    dependencies=[Depends(get_current_user)]
)

UPLOAD_DIR = Path("./app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)



@router.put("")
async def update_image(
        image_id: int,
        update_data: ImageUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    image_db = await db.execute(select(Image).where(Image.id == image_id))
    image = image_db.scalar()
    if not image:
        return HTTPException(
            status_code=404,
            detail="image not found",
        )

    if image.user_id == user.id:
        cache_key = f"image_data: {image_id}"
        cache_data = await redis_client.get(cache_key)

        if cache_data:
            new_data = {
                "user_id": user.id,
                "name": update_data.name,
                "file_path": image.file_path,
                "tags": update_data.tags,
            }
            await redis_client.set(cache_key, json.dumps(new_data), 3600)

        if update_data.name:
            image.name = update_data.name

        if hasattr(image, "tags") and update_data.tags is not None:
            image.tags = update_data.tags

        await db.commit()
        await db.refresh(image)

        return {
                "user_id": user.id,
                "name": update_data.name,
                "file_path": image.file_path,
                "tags": update_data.tags,
            }