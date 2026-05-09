from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dev import get_current_user
from app.db.session import get_db
from app.models.db import User
from app.models.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users", response_model=list[UserResponse])
async def list_seed_users(
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """시드 유저 리스트 (프론트 로그인 화면용)."""
    result = await db.execute(select(User).order_by(User.created_at))
    return list(result.scalars().all())


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
