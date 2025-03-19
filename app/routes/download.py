from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..db.database import  get_db
from ..db.models import ChangedImages, Image, User
from app.services.auth import get_current_user
from pathlib import Path
from app.core.redis_client import redis_client
import json

UPLOAD_DIR = Path("./app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(
    prefix="/download",
    tags=["download image"],
    dependencies=[Depends(get_current_user)]
)



@router.get("")
async def download_image(
        image_id: int,
        image_type: str = Query("grey", enum=["grey", "resized"]),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    get_image_db = await db.execute(select(ChangedImages).where(ChangedImages.image_id == image_id))
    image_db = get_image_db.scalar()

    if not image_db:
        raise HTTPException(
            status_code=404,
            detail="image not found"
        )

    if image_db.user_id == user.id:

        cache_key = f"changed_data: {image_id}"
        cached_data = await redis_client.get(cache_key)

        if cached_data:
            try:
                dict_cached_data = json.loads(cached_data)
                changed_data = {
                    "name": dict_cached_data["name"],
                    "resized_file_path": dict_cached_data["resized_file_path"],
                    "grey_file_path": dict_cached_data["grey_file_path"],
                }
            except (json.JSONDecodeError, TypeError):
                changed_data = None
        else:
            changed_data = None


        if cached_data is None:
            changed_image_db = await db.execute(select(ChangedImages).where(ChangedImages.image_id == image_id))
            original_image_db = await db.execute(select(Image).where(Image.id == image_id))

            changed_image = changed_image_db.scalar()
            original_image = original_image_db.scalar()

            if not changed_image:
                raise HTTPException(
                    status_code=404,
                    detail="image not found"
                )

            changed_data = {
                "name": original_image.name,
                "resized_file_path": changed_image.resized_file_path,
                "grey_file_path": changed_image.grey_file_path,
            }

        file_path = changed_data["grey_file_path"] if image_type == "grey" else changed_data["resized_file_path"]

        return FileResponse(path=file_path, filename=changed_data["name"], media_type="image/jpeg")

    return {
        "error": "you don't have permission to download this image"
    }