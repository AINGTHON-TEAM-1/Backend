from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dev import get_current_user
from app.db.session import get_db
from app.models.db import User
from app.models.schemas.community import (
    CommunityCategory,
    CommunityPostCreate,
    CommunityPostListResponse,
    CommunityPostResponse,
)
from app.services import community_service

router = APIRouter(prefix="/community", tags=["community"])


@router.post(
    "/posts",
    response_model=CommunityPostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    data: CommunityPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommunityPostResponse:
    post = await community_service.create_post(
        user_id=current_user.id, data=data, db=db
    )
    return CommunityPostResponse(
        id=post.id,
        user_id=post.user_id,
        title=post.title,
        body=post.body,
        category=post.category,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author_nickname=current_user.nickname,
    )


@router.get("/posts", response_model=CommunityPostListResponse)
async def list_posts(
    category: CommunityCategory | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CommunityPostListResponse:
    total, items = await community_service.list_posts(
        category=category, page=page, size=size, db=db
    )
    return CommunityPostListResponse(
        total=total,
        page=page,
        items=[CommunityPostResponse(**item) for item in items],
    )


@router.get("/posts/{post_id}", response_model=CommunityPostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CommunityPostResponse:
    item = await community_service.get_post(post_id=post_id, db=db)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return CommunityPostResponse(**item)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await community_service.delete_post(
            post_id=post_id, user_id=current_user.id, db=db
        )
    except community_service.CommunityPostNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        ) from exc
    except community_service.NotOwner as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not the owner of this post"
        ) from exc
