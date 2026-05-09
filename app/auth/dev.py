from __future__ import annotations

import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.db import User


async def get_current_user(
    x_user_id: uuid.UUID | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header required",
        )
    user = await db.get(User, x_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def get_current_user_optional(
    x_user_id: uuid.UUID | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if x_user_id is None:
        return None
    return await db.get(User, x_user_id)
