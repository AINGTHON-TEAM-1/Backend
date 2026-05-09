from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dev import get_current_user
from app.db.session import get_db
from app.models.db import User
from app.models.schemas.post import (
    TakerPostCreate,
    TakerPostResponse,
    TakerPostUpdate,
)
from app.services import post_service
from app.services.post_service import NotOwner, PostNotFound

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "",
    response_model=TakerPostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    data: TakerPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TakerPostResponse:
    post = await post_service.create_post(
        user_id=current_user.id, data=data, db=db
    )
    return TakerPostResponse.model_validate(post)


@router.get("/{post_id}", response_model=TakerPostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TakerPostResponse:
    """공개 엔드포인트 — 인증 불필요."""
    post = await post_service.get_post(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return TakerPostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=TakerPostResponse)
async def update_post(
    post_id: uuid.UUID,
    data: TakerPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TakerPostResponse:
    try:
        post = await post_service.update_post(
            post_id=post_id, user_id=current_user.id, data=data, db=db
        )
    except PostNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        ) from exc
    except NotOwner as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own post",
        ) from exc
    return TakerPostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await post_service.delete_post(
            post_id=post_id, user_id=current_user.id, db=db
        )
    except PostNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        ) from exc
    except NotOwner as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own post",
        ) from exc
