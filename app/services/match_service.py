from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GiverProfile, Match, TakerPost, User
from app.models.schemas.match import MatchCreate
from app.services.giver_service import get_profile_by_user_id
from app.services.pricing import recalculate_giver_pricing

MY_MATCHES_LIMIT = 100


class MatchNotFound(Exception):
    pass


class MatchPermissionDenied(Exception):
    pass


class MatchInvalidState(Exception):
    pass


class DuplicateMatch(Exception):
    pass


class TargetNotFound(Exception):
    pass


def _payment_amount_for(format_: str, profile: GiverProfile) -> int:
    if format_ == "freechat":
        return 0
    if format_ == "coffeechat":
        return profile.coffeechat_price
    if format_ == "mealchat":
        return profile.mealchat_price
    return 0


async def create_match(
    *,
    current_user: User,
    data: MatchCreate,
    db: AsyncSession,
) -> Match:
    if data.target_type == "giver":
        giver_user_id = data.target_id
        taker_user_id = current_user.id
        initiated_by = "taker"
        taker_post_id: uuid.UUID | None = data.post_id

        if taker_post_id is not None:
            owned_post = await db.get(TakerPost, taker_post_id)
            if owned_post is None or owned_post.user_id != taker_user_id:
                raise TargetNotFound()
    else:
        target_post = await db.get(TakerPost, data.target_id)
        if target_post is None:
            raise TargetNotFound()
        giver_user_id = current_user.id
        taker_user_id = target_post.user_id
        initiated_by = "giver"
        taker_post_id = target_post.id

    profile = await get_profile_by_user_id(giver_user_id, db)
    if profile is None:
        raise TargetNotFound()

    dup_stmt = select(Match.id).where(
        and_(
            Match.taker_id == taker_user_id,
            Match.giver_id == giver_user_id,
            Match.status == "pending",
        )
    )
    if (await db.execute(dup_stmt)).first() is not None:
        raise DuplicateMatch()

    match = Match(
        taker_id=taker_user_id,
        giver_id=giver_user_id,
        taker_post_id=taker_post_id,
        initiated_by=initiated_by,
        format=data.format,
        message=data.message,
        preferred_dates=data.preferred_dates,
        payment_amount=_payment_amount_for(data.format, profile),
    )
    db.add(match)

    if initiated_by == "giver" and taker_post_id is not None:
        # 동시 신청 시 카운터 race 방지를 위한 원자적 증가
        await db.execute(
            update(TakerPost)
            .where(TakerPost.id == taker_post_id)
            .values(application_count=TakerPost.application_count + 1)
        )

    await db.commit()
    await db.refresh(match)
    return match


def _can_respond(match: Match, current_user: User) -> bool:
    if match.initiated_by == "taker":
        return match.giver_id == current_user.id
    if match.initiated_by == "giver":
        return match.taker_id == current_user.id
    return False


async def accept_match(
    *,
    match_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Match:
    match = await db.get(Match, match_id)
    if match is None:
        raise MatchNotFound()
    if match.status != "pending":
        raise MatchInvalidState()
    if not _can_respond(match, current_user):
        raise MatchPermissionDenied()

    match.status = "accepted"
    match.accepted_at = datetime.now(timezone.utc)

    if match.taker_post_id is not None:
        await db.execute(
            update(TakerPost)
            .where(TakerPost.id == match.taker_post_id)
            .values(status="matched")
        )

    await db.commit()
    await db.refresh(match)
    return match


async def reject_match(
    *,
    match_id: uuid.UUID,
    current_user: User,
    reason: str,
    db: AsyncSession,
) -> Match:
    match = await db.get(Match, match_id)
    if match is None:
        raise MatchNotFound()
    if match.status != "pending":
        raise MatchInvalidState()
    if not _can_respond(match, current_user):
        raise MatchPermissionDenied()

    match.status = "rejected"

    if match.initiated_by == "giver" and match.taker_post_id is not None:
        # 0 미만으로 떨어지지 않도록 GREATEST로 가드
        await db.execute(
            update(TakerPost)
            .where(TakerPost.id == match.taker_post_id)
            .values(
                application_count=func.greatest(
                    TakerPost.application_count - 1, 0
                )
            )
        )

    await db.commit()
    await db.refresh(match)
    return match


async def pay_match(
    *,
    match_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Match:
    match = await db.get(Match, match_id)
    if match is None:
        raise MatchNotFound()
    if match.status != "accepted":
        raise MatchInvalidState()
    if match.taker_id != current_user.id:
        raise MatchPermissionDenied()

    if match.format != "freechat":
        # PRD FR-FLOW-03: 결제 모킹 — 2초 로딩 후 임의 payment_id 발급
        await asyncio.sleep(2)
        match.payment_id = f"mock_{uuid.uuid4().hex[:8]}"

    match.status = "paid"
    match.paid_at = datetime.now(timezone.utc)

    profile_stmt = (
        select(GiverProfile)
        .where(GiverProfile.user_id == match.giver_id)
        .with_for_update()
    )
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    if profile is not None:
        profile.match_count += 1
        profile.is_newbie = profile.match_count < 3
        coffee, meal = recalculate_giver_pricing(
            profile.match_count, float(profile.rating_avg)
        )
        profile.coffeechat_price = coffee
        profile.mealchat_price = meal
        profile.pricing_updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(match)
    return match


async def get_my_matches(
    *,
    current_user: User,
    kind: str | None,
    db: AsyncSession,
) -> list[Match]:
    me = current_user.id
    sent = and_(
        or_(
            and_(Match.initiated_by == "taker", Match.taker_id == me),
            and_(Match.initiated_by == "giver", Match.giver_id == me),
        )
    )
    received = and_(
        or_(
            and_(Match.initiated_by == "taker", Match.giver_id == me),
            and_(Match.initiated_by == "giver", Match.taker_id == me),
        )
    )

    if kind == "sent":
        condition = sent
    elif kind == "received":
        condition = received
    elif kind == "matched":
        condition = and_(
            or_(Match.taker_id == me, Match.giver_id == me),
            Match.status.in_(["accepted", "paid", "completed"]),
        )
    else:
        condition = or_(Match.taker_id == me, Match.giver_id == me)

    stmt = (
        select(Match)
        .where(condition)
        .order_by(Match.created_at.desc())
        .limit(MY_MATCHES_LIMIT)
    )
    return list((await db.execute(stmt)).scalars().all())
