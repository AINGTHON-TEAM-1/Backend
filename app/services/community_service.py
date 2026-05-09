from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import CommunityPost, User
from app.models.schemas.community import CommunityPostCreate


class CommunityPostNotFound(Exception):
    pass


class NotOwner(Exception):
    pass


async def create_post(
    *,
    user_id: UUID,
    data: CommunityPostCreate,
    db: AsyncSession,
) -> CommunityPost:
    post = CommunityPost(
        user_id=user_id,
        title=data.title,
        body=data.body,
        category=data.category,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def list_posts(
    *,
    category: str | None,
    page: int,
    size: int,
    db: AsyncSession,
) -> tuple[int, list[dict]]:
    base_select = select(CommunityPost.id).join(User, User.id == CommunityPost.user_id)
    if category is not None:
        base_select = base_select.where(CommunityPost.category == category)

    count_stmt = select(func.count()).select_from(base_select.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    rows_select = (
        select(
            CommunityPost.id,
            CommunityPost.user_id,
            CommunityPost.title,
            CommunityPost.body,
            CommunityPost.category,
            CommunityPost.created_at,
            CommunityPost.updated_at,
            User.nickname.label("author_nickname"),
        )
        .join(User, User.id == CommunityPost.user_id)
    )
    if category is not None:
        rows_select = rows_select.where(CommunityPost.category == category)

    rows_select = (
        rows_select.order_by(desc(CommunityPost.created_at))
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = (await db.execute(rows_select)).all()

    items: list[dict] = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "title": r.title,
            "body": r.body,
            "category": r.category,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "author_nickname": r.author_nickname,
        }
        for r in rows
    ]
    return total, items


async def get_post(*, post_id: UUID, db: AsyncSession) -> dict | None:
    stmt = (
        select(
            CommunityPost.id,
            CommunityPost.user_id,
            CommunityPost.title,
            CommunityPost.body,
            CommunityPost.category,
            CommunityPost.created_at,
            CommunityPost.updated_at,
            User.nickname.label("author_nickname"),
        )
        .join(User, User.id == CommunityPost.user_id)
        .where(CommunityPost.id == post_id)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        return None
    return {
        "id": row.id,
        "user_id": row.user_id,
        "title": row.title,
        "body": row.body,
        "category": row.category,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
        "author_nickname": row.author_nickname,
    }


async def delete_post(*, post_id: UUID, user_id: UUID, db: AsyncSession) -> None:
    post = await db.get(CommunityPost, post_id)
    if post is None:
        raise CommunityPostNotFound()
    if post.user_id != user_id:
        raise NotOwner()
    await db.delete(post)
    await db.commit()
