from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db import GiverExperience, GiverProfile, Tag
from app.models.schemas.giver import (
    GiverExperienceCreate,
    GiverProfileCreate,
    GiverProfileUpdate,
)
from app.services.pricing import recalculate_giver_pricing

GIVER_TAG_OWNER = "giver_profile"


class ProfileAlreadyExists(Exception):
    pass


class ProfileNotFound(Exception):
    pass


class ExperienceAlreadyExists(Exception):
    pass


async def create_profile(
    *,
    user_id: uuid.UUID,
    data: GiverProfileCreate,
    db: AsyncSession,
) -> GiverProfile:
    """신규 Giver 프로필 등록.

    PRD FR-GIVER-03: 가격은 시스템 자동 산정 — match_count=0 → 하한선.
    user_id는 giver_profiles.user_id에 UNIQUE 제약 → 중복 시 IntegrityError → ProfileAlreadyExists.
    """
    coffee_price, meal_price = recalculate_giver_pricing(0, 0.0)
    profile = GiverProfile(
        user_id=user_id,
        bio_short=data.bio_short,
        bio_long=data.bio_long,
        freechat_enabled=data.freechat_enabled,
        coffeechat_enabled=data.coffeechat_enabled,
        mealchat_enabled=data.mealchat_enabled,
        coffeechat_price=coffee_price,
        mealchat_price=meal_price,
    )
    db.add(profile)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise ProfileAlreadyExists() from exc
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_profile_by_user_id(
    user_id: uuid.UUID, db: AsyncSession
) -> GiverProfile | None:
    stmt = (
        select(GiverProfile)
        .where(GiverProfile.user_id == user_id)
        .options(selectinload(GiverProfile.experiences))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_profile(
    *,
    user_id: uuid.UUID,
    data: GiverProfileUpdate,
    db: AsyncSession,
) -> GiverProfile:
    profile = await get_profile_by_user_id(user_id, db)
    if profile is None:
        raise ProfileNotFound()

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


async def add_experience(
    *,
    user_id: uuid.UUID,
    data: GiverExperienceCreate,
    db: AsyncSession,
) -> GiverExperience:
    """MVP: Giver당 1개의 경험만 허용 (PRD FR-GIVER-02 'MVP에서는 1개 경험만')."""
    profile = await get_profile_by_user_id(user_id, db)
    if profile is None:
        raise ProfileNotFound()
    if profile.experiences:
        raise ExperienceAlreadyExists()

    experience = GiverExperience(
        giver_profile_id=profile.id,
        community_name=data.community_name,
        categories=list(data.categories),
        duration_months=data.duration_months,
        max_member_count=data.max_member_count,
        proof_url=data.proof_url,
        achievement=data.achievement,
    )
    db.add(experience)
    await db.commit()
    await db.refresh(experience)
    return experience


async def save_tags(
    *,
    owner_type: str,
    owner_id: uuid.UUID,
    tags: Sequence[str],
    is_ai_suggested: bool,
    db: AsyncSession,
) -> None:
    """공통 태그 저장 헬퍼 (Giver/Taker 양쪽에서 사용).

    트랜잭션 commit은 호출자 책임.
    """
    db.add_all(
        [
            Tag(
                owner_type=owner_type,
                owner_id=owner_id,
                tag=t,
                is_ai_suggested=is_ai_suggested,
            )
            for t in tags
        ]
    )
