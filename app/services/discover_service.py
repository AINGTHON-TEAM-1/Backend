from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GiverExperience, GiverProfile, Tag, TakerPost, User
from app.services.giver_service import GIVER_TAG_OWNER
from app.services.post_service import POST_TAG_OWNER


_GIVER_FORMAT_COLUMN = {
    "freechat": GiverProfile.freechat_enabled,
    "coffeechat": GiverProfile.coffeechat_enabled,
    "mealchat": GiverProfile.mealchat_enabled,
}


async def search_givers(
    q: str | None,
    categories: list[str] | None,
    formats: list[str] | None,
    price_min: int,
    price_max: int,
    rating_min: float,
    tag: str | None,
    sort: str,
    page: int,
    size: int,
    db: AsyncSession,
) -> tuple[int, list[dict]]:
    conditions = []
    needs_experience_join = False

    if q:
        like = f"%{q}%"
        conditions.append(
            or_(
                User.nickname.ilike(like),
                GiverProfile.bio_long.ilike(like),
                GiverExperience.community_name.ilike(like),
            )
        )
        needs_experience_join = True

    if categories:
        conditions.append(GiverExperience.categories.overlap(categories))
        needs_experience_join = True

    if formats:
        format_conditions = [
            _GIVER_FORMAT_COLUMN[f].is_(True)
            for f in formats
            if f in _GIVER_FORMAT_COLUMN
        ]
        if format_conditions:
            conditions.append(or_(*format_conditions))

    conditions.append(GiverProfile.coffeechat_price.between(price_min, price_max))
    conditions.append(GiverProfile.rating_avg >= rating_min)

    if tag:
        tag_subq = (
            select(Tag.owner_id)
            .where(
                and_(
                    Tag.owner_type == GIVER_TAG_OWNER,
                    Tag.tag == tag,
                )
            )
            .subquery()
        )
        conditions.append(GiverProfile.id.in_(select(tag_subq.c.owner_id)))

    base_select = select(GiverProfile.id).join(
        User, User.id == GiverProfile.user_id
    )
    if needs_experience_join:
        base_select = base_select.join(
            GiverExperience,
            GiverExperience.giver_profile_id == GiverProfile.id,
            isouter=True,
        )
    if conditions:
        base_select = base_select.where(and_(*conditions))
    base_select = base_select.distinct()

    count_stmt = select(func.count()).select_from(base_select.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    rows_select = (
        select(
            GiverProfile.id,
            GiverProfile.bio_short,
            GiverProfile.rating_avg,
            GiverProfile.rating_count,
            GiverProfile.match_count,
            GiverProfile.freechat_enabled,
            GiverProfile.coffeechat_price,
            GiverProfile.mealchat_price,
            GiverProfile.is_newbie,
            GiverProfile.created_at,
            User.id.label("user_id"),
            User.nickname,
            User.profile_image_url,
        )
        .join(User, User.id == GiverProfile.user_id)
    )
    if needs_experience_join:
        rows_select = rows_select.join(
            GiverExperience,
            GiverExperience.giver_profile_id == GiverProfile.id,
            isouter=True,
        )
    if conditions:
        rows_select = rows_select.where(and_(*conditions))
    rows_select = rows_select.distinct()

    if sort == "rating":
        rows_select = rows_select.order_by(
            desc(GiverProfile.rating_avg), desc(GiverProfile.created_at)
        )
    elif sort == "popular":
        rows_select = rows_select.order_by(
            desc(GiverProfile.match_count), desc(GiverProfile.created_at)
        )
    elif sort == "price_asc":
        rows_select = rows_select.order_by(
            asc(GiverProfile.coffeechat_price), desc(GiverProfile.created_at)
        )
    else:
        # cold-start boost: surface newbie givers first to bootstrap their first match
        rows_select = rows_select.order_by(
            desc(GiverProfile.is_newbie), desc(GiverProfile.created_at)
        )

    rows_select = rows_select.offset((page - 1) * size).limit(size)
    rows = (await db.execute(rows_select)).all()

    if not rows:
        return total, []

    profile_ids: list[UUID] = [r.id for r in rows]

    exp_stmt = select(
        GiverExperience.giver_profile_id, GiverExperience.categories
    ).where(GiverExperience.giver_profile_id.in_(profile_ids))
    exp_rows = (await db.execute(exp_stmt)).all()
    categories_by_profile: dict[UUID, list[str]] = {}
    for pid, cats in exp_rows:
        if not cats:
            continue
        bucket = categories_by_profile.setdefault(pid, [])
        for c in cats:
            if c not in bucket:
                bucket.append(c)

    tag_stmt = select(Tag.owner_id, Tag.tag).where(
        and_(
            Tag.owner_type == GIVER_TAG_OWNER,
            Tag.owner_id.in_(profile_ids),
        )
    )
    tag_rows = (await db.execute(tag_stmt)).all()
    tags_by_profile: dict[UUID, list[str]] = {}
    for owner_id, t in tag_rows:
        bucket = tags_by_profile.setdefault(owner_id, [])
        if t not in bucket:
            bucket.append(t)

    items: list[dict] = []
    for r in rows:
        items.append(
            {
                "id": r.id,
                "nickname": r.nickname,
                "profile_image_url": r.profile_image_url,
                "bio_short": r.bio_short,
                "rating_avg": r.rating_avg,
                "rating_count": r.rating_count,
                "match_count": r.match_count,
                "tags": tags_by_profile.get(r.id, []),
                "categories": categories_by_profile.get(r.id, []),
                "freechat_enabled": r.freechat_enabled,
                "coffeechat_price": r.coffeechat_price,
                "mealchat_price": r.mealchat_price,
            }
        )

    return total, items


async def search_posts(
    q: str | None,
    categories: list[str] | None,
    formats: list[str] | None,
    budget_min: int | None,
    budget_max: int | None,
    active_only: bool,
    tag: str | None,
    sort: str,
    page: int,
    size: int,
    db: AsyncSession,
) -> tuple[int, list[dict]]:
    conditions = []

    if q:
        tsv = func.to_tsvector(
            "simple",
            func.coalesce(TakerPost.title, "") + " " + func.coalesce(TakerPost.body, ""),
        )
        conditions.append(tsv.op("@@")(func.plainto_tsquery("simple", q)))

    if categories:
        conditions.append(TakerPost.category.in_(categories))

    if formats:
        conditions.append(TakerPost.preferred_format.in_(formats))

    if budget_min is not None:
        conditions.append(TakerPost.budget_max.is_not(None))
        conditions.append(TakerPost.budget_max >= budget_min)

    if budget_max is not None:
        conditions.append(TakerPost.budget_min.is_not(None))
        conditions.append(TakerPost.budget_min <= budget_max)

    if active_only:
        conditions.append(TakerPost.status == "open")

    if tag:
        tag_subq = (
            select(Tag.owner_id)
            .where(
                and_(
                    Tag.owner_type == POST_TAG_OWNER,
                    Tag.tag == tag,
                )
            )
            .subquery()
        )
        conditions.append(TakerPost.id.in_(select(tag_subq.c.owner_id)))

    base_select = select(TakerPost.id).join(User, User.id == TakerPost.user_id)
    if conditions:
        base_select = base_select.where(and_(*conditions))
    base_select = base_select.distinct()

    count_stmt = select(func.count()).select_from(base_select.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    rows_select = select(
        TakerPost.id,
        TakerPost.title,
        TakerPost.body,
        TakerPost.category,
        TakerPost.preferred_format,
        TakerPost.budget_min,
        TakerPost.budget_max,
        TakerPost.application_count,
        TakerPost.status,
        TakerPost.created_at,
        User.nickname.label("author_nickname"),
    ).join(User, User.id == TakerPost.user_id)
    if conditions:
        rows_select = rows_select.where(and_(*conditions))
    rows_select = rows_select.distinct()

    if sort == "applications_asc":
        rows_select = rows_select.order_by(
            asc(TakerPost.application_count), desc(TakerPost.created_at)
        )
    elif sort == "budget_desc":
        rows_select = rows_select.order_by(
            desc(TakerPost.budget_max), desc(TakerPost.created_at)
        )
    else:
        rows_select = rows_select.order_by(desc(TakerPost.created_at))

    rows_select = rows_select.offset((page - 1) * size).limit(size)
    rows = (await db.execute(rows_select)).all()

    if not rows:
        return total, []

    post_ids: list[UUID] = [r.id for r in rows]

    tag_stmt = select(Tag.owner_id, Tag.tag).where(
        and_(
            Tag.owner_type == POST_TAG_OWNER,
            Tag.owner_id.in_(post_ids),
        )
    )
    tag_rows = (await db.execute(tag_stmt)).all()
    tags_by_post: dict[UUID, list[str]] = {}
    for owner_id, t in tag_rows:
        bucket = tags_by_post.setdefault(owner_id, [])
        if t not in bucket:
            bucket.append(t)

    items: list[dict] = []
    for r in rows:
        body = r.body or ""
        items.append(
            {
                "id": r.id,
                "title": r.title,
                "body_preview": body[:120],
                "category": r.category,
                "preferred_format": r.preferred_format,
                "budget_min": r.budget_min,
                "budget_max": r.budget_max,
                "tags": tags_by_post.get(r.id, []),
                "application_count": r.application_count,
                "status": r.status,
                "author_nickname": r.author_nickname,
                "created_at": r.created_at,
            }
        )

    return total, items


async def get_popular_tags(db: AsyncSession, limit: int = 10) -> list[dict]:
    stmt = (
        select(Tag.tag, func.count().label("cnt"))
        .where(Tag.created_at >= func.now() - timedelta(days=30))
        .group_by(Tag.tag)
        .order_by(desc("cnt"))
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [{"tag": tag, "count": cnt} for tag, cnt in rows]
