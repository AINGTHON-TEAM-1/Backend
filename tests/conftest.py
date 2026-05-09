"""테스트 픽스처.

테스트 DB는 별도(`giverun_test`)이고 마이그레이션이 미리 적용되어 있어야 한다.
각 테스트 함수마다 truncate 후 실행 (격리).
"""

from __future__ import annotations

import os

# Settings 캐시가 먼저 잡히는 것을 막기 위해 import 전에 환경변수 강제
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/giverun_test",
)

from collections.abc import AsyncGenerator  # noqa: E402

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.db import GiverProfile, TakerPost, User  # noqa: E402

TEST_DB_URL = os.environ["DATABASE_URL"]

# NullPool: 매 연결마다 새로 — pytest-asyncio loop scope와 asyncpg 풀 캐시 충돌 회피 (Windows)
_engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
_TestSession = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def _truncate_db() -> AsyncGenerator[None, None]:
    async with _engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE community_posts, matches, tags, giver_experiences, "
                "giver_profiles, taker_posts, users RESTART IDENTITY CASCADE"
            )
        )
    yield


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with _TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def make_taker(db: AsyncSession, *, nickname: str = "T") -> User:
    user = User(nickname=nickname, role="taker", email=f"{nickname}@t.test")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def make_giver(
    db: AsyncSession,
    *,
    nickname: str = "G",
    coffee: int = 5000,
    meal: int = 10000,
    rating_avg: float = 0.0,
    rating_count: int = 0,
    match_count: int = 0,
    is_newbie: bool = True,
) -> tuple[User, GiverProfile]:
    user = User(nickname=nickname, role="giver", email=f"{nickname}@g.test")
    db.add(user)
    await db.flush()
    profile = GiverProfile(
        user_id=user.id,
        bio_short=f"{nickname}_short",
        bio_long=f"{nickname}_long bio",
        freechat_enabled=True,
        coffeechat_enabled=True,
        mealchat_enabled=True,
        coffeechat_price=coffee,
        mealchat_price=meal,
        rating_avg=rating_avg,
        rating_count=rating_count,
        match_count=match_count,
        is_newbie=is_newbie,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(user)
    await db.refresh(profile)
    return user, profile


async def make_post(
    db: AsyncSession,
    *,
    user_id,
    title: str = "도와주세요",
    body: str = "도움이 필요합니다",
    category: str | None = "community",
    preferred_format: str | None = "coffeechat",
    budget_min: int | None = 5000,
    budget_max: int | None = 15000,
) -> TakerPost:
    post = TakerPost(
        user_id=user_id,
        title=title,
        body=body,
        category=category,
        preferred_format=preferred_format,
        budget_min=budget_min,
        budget_max=budget_max,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post
