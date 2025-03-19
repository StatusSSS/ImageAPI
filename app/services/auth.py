from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from app.db.database import get_db
from app.core.security import decode_access_token



security = HTTPBearer()

async def get_user_from_db(db: AsyncSession, username: str):
    user = await db.execute(select(User).where(User.username == username))
    return user.scalars().first()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    username = payload.get("sub")
    user = await get_user_from_db(db, username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user



