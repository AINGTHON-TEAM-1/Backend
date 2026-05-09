"""양방향 탐색 통합 테스트 (PRD §8.4)."""

from __future__ import annotations

import time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GiverExperience, Tag
from tests.conftest import make_giver, make_post, make_taker


@pytest.mark.asyncio
async def test_discover_givers_default_list(client: AsyncClient, db: AsyncSession) -> None:
    await make_giver(db, nickname="newbieG")
    await make_giver(db, nickname="popularG", match_count=30, is_newbie=False, rating_avg=4.8)

    resp = await client.get("/api/v1/discover/givers")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert {item["nickname"] for item in body["items"]} == {"newbieG", "popularG"}


@pytest.mark.asyncio
async def test_discover_givers_text_search(client: AsyncClient, db: AsyncSession) -> None:
    user_a, profile_a = await make_giver(db, nickname="디스코드운영러")
    user_b, _ = await make_giver(db, nickname="피지컬개발자")

    db.add(
        GiverExperience(
            giver_profile_id=profile_a.id,
            community_name="프론트엔드 디스코드",
            categories=["community"],
        )
    )
    await db.commit()

    resp = await client.get("/api/v1/discover/givers", params={"q": "디스코드"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    nicknames = [i["nickname"] for i in items]
    assert "디스코드운영러" in nicknames
    assert "피지컬개발자" not in nicknames


@pytest.mark.asyncio
async def test_discover_givers_category_filter(
    client: AsyncClient, db: AsyncSession
) -> None:
    user_a, profile_a = await make_giver(db, nickname="circleG")
    user_b, profile_b = await make_giver(db, nickname="partyG")
    db.add(GiverExperience(giver_profile_id=profile_a.id, categories=["circle"]))
    db.add(GiverExperience(giver_profile_id=profile_b.id, categories=["party"]))
    await db.commit()

    resp = await client.get("/api/v1/discover/givers", params={"categories": "circle"})
    assert resp.status_code == 200
    nicknames = [i["nickname"] for i in resp.json()["items"]]
    assert nicknames == ["circleG"]


@pytest.mark.asyncio
async def test_discover_givers_sort_by_rating(
    client: AsyncClient, db: AsyncSession
) -> None:
    await make_giver(db, nickname="lowG", rating_avg=3.0, rating_count=5, match_count=5, is_newbie=False)
    await make_giver(db, nickname="highG", rating_avg=4.9, rating_count=20, match_count=20, is_newbie=False)
    await make_giver(db, nickname="midG", rating_avg=4.0, rating_count=10, match_count=10, is_newbie=False)

    resp = await client.get("/api/v1/discover/givers", params={"sort": "rating"})
    nicknames = [i["nickname"] for i in resp.json()["items"]]
    assert nicknames == ["highG", "midG", "lowG"]


@pytest.mark.asyncio
async def test_discover_givers_cold_start_boost(
    client: AsyncClient, db: AsyncSession
) -> None:
    """`latest` 정렬 시 신규 Giver 우선 노출."""
    await make_giver(db, nickname="vetG", is_newbie=False, match_count=30, rating_avg=4.8)
    await make_giver(db, nickname="newG", is_newbie=True, match_count=0)

    resp = await client.get("/api/v1/discover/givers", params={"sort": "latest"})
    nicknames = [i["nickname"] for i in resp.json()["items"]]
    assert nicknames[0] == "newG"


@pytest.mark.asyncio
async def test_discover_posts_default_and_fts(
    client: AsyncClient, db: AsyncSession
) -> None:
    taker = await make_taker(db, nickname="taker1")
    await make_post(
        db,
        user_id=taker.id,
        title="알고리즘 동아리 운영 도움",
        body="신학기 알고리즘 스터디 살리기",
    )
    await make_post(
        db,
        user_id=taker.id,
        title="요리 모임 활성화",
        body="음식 동아리 회원 늘리기",
    )

    list_resp = await client.get("/api/v1/discover/posts")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 2

    fts_resp = await client.get("/api/v1/discover/posts", params={"q": "알고리즘"})
    titles = [p["title"] for p in fts_resp.json()["items"]]
    assert any("알고리즘" in t for t in titles)
    assert all("요리" not in t for t in titles)


@pytest.mark.asyncio
async def test_discover_posts_blue_ocean_sort(
    client: AsyncClient, db: AsyncSession
) -> None:
    taker = await make_taker(db, nickname="taker2")
    p_low = await make_post(db, user_id=taker.id, title="신청 적은 글")
    p_high = await make_post(db, user_id=taker.id, title="신청 많은 글")

    p_low.application_count = 0
    p_high.application_count = 10
    await db.commit()

    resp = await client.get(
        "/api/v1/discover/posts", params={"sort": "applications_asc"}
    )
    titles = [p["title"] for p in resp.json()["items"]]
    assert titles[0] == "신청 적은 글"


@pytest.mark.asyncio
async def test_discover_popular_tags(client: AsyncClient, db: AsyncSession) -> None:
    user, profile = await make_giver(db, nickname="g")
    db.add_all(
        [
            Tag(owner_type="giver_profile", owner_id=profile.id, tag="리텐션"),
            Tag(owner_type="giver_profile", owner_id=profile.id, tag="리텐션"),
            Tag(owner_type="giver_profile", owner_id=profile.id, tag="신입유치"),
        ]
    )
    await db.commit()

    resp = await client.get("/api/v1/discover/popular-tags")
    assert resp.status_code == 200
    tags = {row["tag"]: row["count"] for row in resp.json()["tags"]}
    assert tags.get("리텐션") == 2
    assert tags.get("신입유치") == 1


@pytest.mark.asyncio
async def test_discover_response_time_under_1s(
    client: AsyncClient, db: AsyncSession
) -> None:
    """PRD §11.1 KPI: 시드 데이터 기준 < 1초."""
    for i in range(5):
        await make_giver(db, nickname=f"g{i}")
    taker = await make_taker(db, nickname="t")
    for i in range(5):
        await make_post(db, user_id=taker.id, title=f"post{i}")

    start = time.perf_counter()
    resp = await client.get("/api/v1/discover/givers")
    elapsed = time.perf_counter() - start
    assert resp.status_code == 200
    assert elapsed < 1.0, f"discover/givers took {elapsed:.3f}s"
