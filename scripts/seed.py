"""시드 데이터 — Giver 5명 + Taker 구인글 5건 + 태그.

PRD §10.2 P0 데모 필수.
멱등(idempotent): 모든 시드 데이터는 매번 truncate 후 재삽입.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.db import (
    GiverExperience,
    GiverProfile,
    Tag,
    TakerPost,
    User,
)


GIVER_SEEDS = [
    {
        "nickname": "신규Giver",
        "email": "newbie@example.com",
        "bio_short": "첫 시작을 응원합니다",
        "bio_long": "이제 막 시작하지만 진심으로 도와드릴게요.",
        "rating_avg": Decimal("0.00"),
        "rating_count": 0,
        "match_count": 0,
        "is_newbie": True,
        "coffeechat_price": 5000,
        "mealchat_price": 10000,
        "pricing_score": Decimal("0.00"),
        "experience": {
            "community_name": "스타트업 사이드 모임",
            "categories": ["crew", "community"],
            "duration_months": 3,
            "max_member_count": 8,
            "achievement": "주간 정기 모임 운영",
        },
        "tags": ["사이드프로젝트", "스타트업"],
    },
    {
        "nickname": "입문Giver",
        "email": "rookie@example.com",
        "bio_short": "동아리 운영 노하우 공유",
        "bio_long": "학부 동아리에서 1년 이상 부장을 맡으며 배운 것들.",
        "rating_avg": Decimal("4.00"),
        "rating_count": 4,
        "match_count": 5,
        "is_newbie": True,
        "coffeechat_price": 8500,
        "mealchat_price": 16000,
        "pricing_score": Decimal("0.30"),
        "experience": {
            "community_name": "학부 알고리즘 동아리",
            "categories": ["circle", "league"],
            "duration_months": 14,
            "max_member_count": 25,
            "achievement": "교내 알고리즘 대회 본선 진출",
        },
        "tags": ["동아리운영", "스터디", "대학생"],
    },
    {
        "nickname": "활성Giver",
        "email": "active@example.com",
        "bio_short": "100명 디스코드 1년 운영",
        "bio_long": "활동 지속률 60% 유지를 위한 실전 노하우.",
        "rating_avg": Decimal("4.50"),
        "rating_count": 12,
        "match_count": 15,
        "is_newbie": False,
        "coffeechat_price": 14000,
        "mealchat_price": 28000,
        "pricing_score": Decimal("0.55"),
        "experience": {
            "community_name": "프론트엔드 디스코드",
            "categories": ["network", "community"],
            "duration_months": 18,
            "max_member_count": 120,
            "achievement": "정기 행사 12회 주최, 월간 활성 60%+",
        },
        "tags": ["디스코드", "프론트엔드", "커뮤니티운영", "정기행사"],
    },
    {
        "nickname": "인기Giver",
        "email": "popular@example.com",
        "bio_short": "300명 컨퍼런스 호스트",
        "bio_long": "오프라인 행사 기획·운영 전문.",
        "rating_avg": Decimal("4.80"),
        "rating_count": 28,
        "match_count": 30,
        "is_newbie": False,
        "coffeechat_price": 23000,
        "mealchat_price": 45000,
        "pricing_score": Decimal("0.85"),
        "experience": {
            "community_name": "테크 컨퍼런스 GDGoC",
            "categories": ["network", "party"],
            "duration_months": 24,
            "max_member_count": 300,
            "achievement": "연 2회 컨퍼런스 운영, 누적 1500명 참여",
        },
        "tags": ["컨퍼런스", "오프라인행사", "GDGoC", "기획", "운영"],
    },
    {
        "nickname": "저평점Giver",
        "email": "lowrating@example.com",
        "bio_short": "다수 매칭 경험",
        "bio_long": "다양한 시도와 실수에서 배운 점을 공유합니다.",
        "rating_avg": Decimal("3.20"),
        "rating_count": 18,
        "match_count": 20,
        "is_newbie": False,
        "coffeechat_price": 9500,
        "mealchat_price": 18000,
        "pricing_score": Decimal("0.35"),
        "experience": {
            "community_name": "다목적 크루",
            "categories": ["crew"],
            "duration_months": 10,
            "max_member_count": 30,
            "achievement": "다양한 분야의 크루 운영 시도",
        },
        "tags": ["크루", "사이드프로젝트", "운영시도"],
    },
]

TAKER_SEEDS = [
    {
        "nickname": "동아리회장A",
        "email": "circle-a@example.com",
        "post": {
            "title": "신입 모집·이벤트 기획 도와주세요",
            "body": (
                "교내 알고리즘 동아리 회장입니다. 신학기 신입 모집을 어떻게 시작해야 할지, "
                "초기 이벤트 기획 노하우가 필요합니다."
            ),
            "category": "circle",
            "preferred_format": "coffeechat",
            "budget_min": 5000,
            "budget_max": 15000,
        },
        "tags": ["동아리", "신입모집", "이벤트기획"],
    },
    {
        "nickname": "디스코드운영자B",
        "email": "discord-b@example.com",
        "post": {
            "title": "활성율 회복 노하우 필요",
            "body": (
                "100명 규모 디스코드 서버를 운영 중인데 활성율이 30% 아래로 떨어졌습니다. "
                "원인 진단과 회복 전략을 배우고 싶습니다."
            ),
            "category": "community",
            "preferred_format": "mealchat",
            "budget_min": 10000,
            "budget_max": 30000,
        },
        "tags": ["디스코드", "활성율", "커뮤니티"],
    },
    {
        "nickname": "스터디그룹장C",
        "email": "study-c@example.com",
        "post": {
            "title": "참여율 떨어지는 스터디 살리기",
            "body": "주 1회 스터디인데 4주차부터 참여율이 50% 아래입니다. 운영 방식 코칭이 필요합니다.",
            "category": "league",
            "preferred_format": "freechat",
            "budget_min": 0,
            "budget_max": 0,
        },
        "tags": ["스터디", "참여율", "운영코칭"],
    },
    {
        "nickname": "사이드팀장D",
        "email": "side-d@example.com",
        "post": {
            "title": "팀 분위기·생산성 관리 어려워요",
            "body": "5명 사이드 프로젝트 팀장입니다. 팀원 간 온도차가 커서 진척이 더딥니다.",
            "category": "crew",
            "preferred_format": "coffeechat",
            "budget_min": 8000,
            "budget_max": 20000,
        },
        "tags": ["사이드프로젝트", "팀빌딩", "생산성"],
    },
    {
        "nickname": "행사기획E",
        "email": "event-e@example.com",
        "post": {
            "title": "오프라인 행사 처음 기획합니다",
            "body": "200명 규모 오프라인 컨퍼런스 기획·운영 자문이 필요합니다.",
            "category": "party",
            "preferred_format": "mealchat",
            "budget_min": 15000,
            "budget_max": 40000,
        },
        "tags": ["오프라인행사", "컨퍼런스", "기획"],
    },
]


async def _truncate(session: AsyncSession) -> None:
    await session.execute(
        text(
            "TRUNCATE TABLE matches, tags, giver_experiences, giver_profiles, "
            "taker_posts, users RESTART IDENTITY CASCADE"
        )
    )


async def _seed_givers(session: AsyncSession) -> None:
    for spec in GIVER_SEEDS:
        user = User(
            nickname=spec["nickname"],
            email=spec["email"],
            role="giver",
        )
        session.add(user)
        await session.flush()

        profile = GiverProfile(
            user_id=user.id,
            bio_short=spec["bio_short"],
            bio_long=spec["bio_long"],
            freechat_enabled=True,
            coffeechat_enabled=True,
            mealchat_enabled=True,
            coffeechat_price=spec["coffeechat_price"],
            mealchat_price=spec["mealchat_price"],
            pricing_score=spec["pricing_score"],
            rating_avg=spec["rating_avg"],
            rating_count=spec["rating_count"],
            match_count=spec["match_count"],
            is_newbie=spec["is_newbie"],
        )
        session.add(profile)
        await session.flush()

        exp = spec["experience"]
        session.add(
            GiverExperience(
                giver_profile_id=profile.id,
                community_name=exp["community_name"],
                categories=exp["categories"],
                duration_months=exp["duration_months"],
                max_member_count=exp["max_member_count"],
                achievement=exp["achievement"],
            )
        )

        for idx, tag_name in enumerate(spec["tags"]):
            session.add(
                Tag(
                    owner_type="giver_profile",
                    owner_id=profile.id,
                    tag=tag_name,
                    is_ai_suggested=(idx % 2 == 0),
                )
            )


async def _seed_takers(session: AsyncSession) -> None:
    for spec in TAKER_SEEDS:
        user = User(
            nickname=spec["nickname"],
            email=spec["email"],
            role="taker",
        )
        session.add(user)
        await session.flush()

        post_spec = spec["post"]
        post = TakerPost(
            user_id=user.id,
            title=post_spec["title"],
            body=post_spec["body"],
            category=post_spec["category"],
            preferred_format=post_spec["preferred_format"],
            budget_min=post_spec["budget_min"],
            budget_max=post_spec["budget_max"],
        )
        session.add(post)
        await session.flush()

        for idx, tag_name in enumerate(spec["tags"]):
            session.add(
                Tag(
                    owner_type="taker_post",
                    owner_id=post.id,
                    tag=tag_name,
                    is_ai_suggested=(idx % 2 == 0),
                )
            )


async def run() -> None:
    async with AsyncSessionLocal() as session:
        await _truncate(session)
        await _seed_givers(session)
        await _seed_takers(session)
        await session.commit()
    print(
        f"seeded: givers={len(GIVER_SEEDS)}, taker_posts={len(TAKER_SEEDS)}, "
        f"tags={sum(len(s['tags']) for s in GIVER_SEEDS) + sum(len(s['tags']) for s in TAKER_SEEDS)}"
    )


if __name__ == "__main__":
    asyncio.run(run())
