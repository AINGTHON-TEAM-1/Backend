from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import TakerPost
from app.models.schemas.post import TakerPostCreate, TakerPostUpdate

POST_TAG_OWNER = "taker_post"


class PostNotFound(Exception):
    pass


class NotOwner(Exception):
    pass


async def create_post(
    *,
    user_id: uuid.UUID,
    data: TakerPostCreate,
    db: AsyncSession,
) -> TakerPost:
    post = TakerPost(
        user_id=user_id,
        title=data.title,
        body=data.body,
        category=data.category,
        preferred_format=data.preferred_format,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(post_id: uuid.UUID, db: AsyncSession) -> TakerPost | None:
    return await db.get(TakerPost, post_id)


async def update_post(
    *,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    data: TakerPostUpdate,
    db: AsyncSession,
) -> TakerPost:
    post = await db.get(TakerPost, post_id)
    if post is None:
        raise PostNotFound()
    if post.user_id != user_id:
        raise NotOwner()

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(
    *,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    post = await db.get(TakerPost, post_id)
    if post is None:
        raise PostNotFound()
    if post.user_id != user_id:
        raise NotOwner()

    await db.delete(post)
    await db.commit()
