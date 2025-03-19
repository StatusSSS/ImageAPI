from pydantic import BaseModel
from typing import Optional


class ImageUpdate(BaseModel):
    name: Optional[str] = None
    tags: Optional[str] = None


