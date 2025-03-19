from fastapi import Body, APIRouter, Depends, HTTPException
from app.core.security import hash_password
from app.db.models import User
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/register",
    tags=["register user"]
)


@router.post("")
async def register(
        username: str = Body(...),
        user_email: str = Body(...),
        password: str = Body(...),
        db: AsyncSession = Depends(get_db)
):
    hashed_password = hash_password(password)
    new_user = User(username=username, user_email=user_email, user_password=password, hashed_password=hashed_password)

    db.add(new_user)

    try:
        await db.commit()
        return {"message": "user was created successfully"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"message": "user already exists"}
        )
