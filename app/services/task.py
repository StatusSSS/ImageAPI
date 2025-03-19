from app.core.celery_app import celery_app
import asyncio

from app.db.models import Image as ImageModel
from app.db.models import ChangedImages
from app.db.sync_database import SyncSessionLocal

import os
from app.services.image_utils import resize_image_imageio, convert_to_grayscale_imageio

from app.core.redis_client import redis_client
import json


@celery_app.task(name="task.process_image")
def process_image(image_id: int):

    with SyncSessionLocal() as db:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()

        if not image:
            print(f"[X] Image with {image_id} not found")
            return
        print(image)


        image_path = image.file_path
        image_name = image.name
        user_id = image.user_id

        if not os.path.exists(image_path):
            print(f"[X] Image {image_id} Path not found")
            return


        sizes = (100, 100)
        resized_path = resize_image_imageio(image_path, sizes)
        grey_path = convert_to_grayscale_imageio(image_path)


        changed_image = ChangedImages(
            user_id=user_id,
            image_id=image_id,
            resized_file_path=resized_path,
            grey_file_path=grey_path,
        )
        db.add(changed_image)
        db.commit()
        db.refresh(changed_image)


        resized_file_path = changed_image.resized_file_path
        grey_file_path = changed_image.grey_file_path

    changed_data = {
        "name": image_name,
        "resized_file_path": resized_file_path,
        "grey_file_path": grey_file_path,
    }


    cache_key = f"changed_data:{image_id}"
    redis_client.set(cache_key, json.dumps(changed_data), 3600)

    print(f"[✔] Processed image {image_id}: resized, grayscale.")