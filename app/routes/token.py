from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from app.schemas.token_models import GetTokenModel
from app.db.database import  get_db
from app.services.auth import get_user_from_db
from app.core.security import verify_password, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/token",
    tags=["create token"],
)



@router.post("")
async def create_token(
        user_data: GetTokenModel,
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_db(db, user_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}