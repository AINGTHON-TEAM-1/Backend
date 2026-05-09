"""매칭 플로우 통합 테스트 (PRD §8.6, FR-FLOW-01~04)."""

from __future__ import annotations

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GiverProfile, TakerPost
from tests.conftest import make_giver, make_post, make_taker


@pytest.mark.asyncio
async def test_taker_to_giver_full_flow(
    client: AsyncClient, db: AsyncSession
) -> None:
    """시나리오 A: Taker → Giver 신청 → 수락 → 결제."""
    taker = await make_taker(db, nickname="taker_a")
    giver_user, giver_profile = await make_giver(
        db, nickname="giver_a", coffee=8000, meal=16000
    )

    create_resp = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "coffeechat",
            "message": "커피챗 부탁드립니다",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    match = create_resp.json()
    assert match["initiated_by"] == "taker"
    assert match["status"] == "pending"
    assert match["payment_amount"] == 8000

    accept_resp = await client.patch(
        f"/api/v1/matches/{match['id']}/accept",
        headers={"X-User-Id": str(giver_user.id)},
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    pay_resp = await client.post(
        f"/api/v1/matches/{match['id']}/pay",
        headers={"X-User-Id": str(taker.id)},
    )
    assert pay_resp.status_code == 200
    paid = pay_resp.json()
    assert paid["status"] == "paid"
    assert paid["payment_id"].startswith("mock_")
    assert paid["payment_amount"] == 8000


@pytest.mark.asyncio
async def test_giver_to_taker_full_flow(
    client: AsyncClient, db: AsyncSession
) -> None:
    """시나리오 B: Giver → Taker 구인글 신청 → 수락."""
    taker = await make_taker(db, nickname="taker_b")
    post = await make_post(db, user_id=taker.id, title="동아리 운영 도움 필요")
    giver_user, _ = await make_giver(db, nickname="giver_b")

    create_resp = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(giver_user.id)},
        json={
            "target_type": "taker_post",
            "target_id": str(post.id),
            "format": "freechat",
            "message": "도와드리겠습니다",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    match = create_resp.json()
    assert match["initiated_by"] == "giver"
    assert match["taker_post_id"] == str(post.id)
    assert match["payment_amount"] == 0

    await db.refresh(post)
    assert post.application_count == 1

    accept_resp = await client.patch(
        f"/api/v1/matches/{match['id']}/accept",
        headers={"X-User-Id": str(taker.id)},
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    await db.refresh(post)
    assert post.status == "matched"


@pytest.mark.asyncio
async def test_freechat_skip_payment(client: AsyncClient, db: AsyncSession) -> None:
    taker = await make_taker(db, nickname="taker_c")
    giver_user, _ = await make_giver(db, nickname="giver_c")

    create = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "freechat",
            "message": "프리챗 신청",
        },
    )
    match_id = create.json()["id"]
    assert create.json()["payment_amount"] == 0

    await client.patch(
        f"/api/v1/matches/{match_id}/accept",
        headers={"X-User-Id": str(giver_user.id)},
    )
    pay = await client.post(
        f"/api/v1/matches/{match_id}/pay",
        headers={"X-User-Id": str(taker.id)},
    )
    assert pay.json()["status"] == "paid"
    assert pay.json()["payment_id"] is None


@pytest.mark.asyncio
async def test_invalid_state_accept_already_accepted(
    client: AsyncClient, db: AsyncSession
) -> None:
    taker = await make_taker(db, nickname="t_invalid")
    giver_user, _ = await make_giver(db, nickname="g_invalid")

    create = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "freechat",
            "message": "신청",
        },
    )
    match_id = create.json()["id"]
    headers_giver = {"X-User-Id": str(giver_user.id)}
    await client.patch(f"/api/v1/matches/{match_id}/accept", headers=headers_giver)

    again = await client.patch(
        f"/api/v1/matches/{match_id}/accept", headers=headers_giver
    )
    assert again.status_code == 400


@pytest.mark.asyncio
async def test_accept_permission_denied(
    client: AsyncClient, db: AsyncSession
) -> None:
    """신청한 사람이 자기 신청을 수락 시도하면 403."""
    taker = await make_taker(db, nickname="t_perm")
    giver_user, _ = await make_giver(db, nickname="g_perm")

    create = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "freechat",
            "message": "test",
        },
    )
    match_id = create.json()["id"]

    self_accept = await client.patch(
        f"/api/v1/matches/{match_id}/accept",
        headers={"X-User-Id": str(taker.id)},
    )
    assert self_accept.status_code == 403


@pytest.mark.asyncio
async def test_duplicate_pending_match_rejected(
    client: AsyncClient, db: AsyncSession
) -> None:
    taker = await make_taker(db, nickname="t_dup")
    giver_user, _ = await make_giver(db, nickname="g_dup")
    payload = {
        "target_type": "giver",
        "target_id": str(giver_user.id),
        "format": "freechat",
        "message": "first",
    }
    headers = {"X-User-Id": str(taker.id)}
    first = await client.post("/api/v1/matches", headers=headers, json=payload)
    assert first.status_code == 201
    second = await client.post("/api/v1/matches", headers=headers, json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_payment_amount_snapshot_immutable(
    client: AsyncClient, db: AsyncSession
) -> None:
    """결제 후 Giver 가격이 바뀌어도 match.payment_amount는 스냅샷이므로 불변."""
    taker = await make_taker(db, nickname="t_snap")
    giver_user, profile = await make_giver(
        db, nickname="g_snap", coffee=10000, meal=20000
    )

    create = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "coffeechat",
            "message": "test",
        },
    )
    match_id = create.json()["id"]
    assert create.json()["payment_amount"] == 10000

    profile.coffeechat_price = 25000
    await db.commit()

    me = await client.get(
        "/api/v1/matches/me", headers={"X-User-Id": str(taker.id)}
    )
    body = me.json()
    target = next(m for m in body if m["id"] == match_id)
    assert target["payment_amount"] == 10000


@pytest.mark.asyncio
async def test_giver_pricing_recalc_after_paid(
    client: AsyncClient, db: AsyncSession
) -> None:
    """결제 완료 시 giver_profile.match_count 증가 + 가격 재산정."""
    taker = await make_taker(db, nickname="t_recalc")
    giver_user, profile = await make_giver(
        db,
        nickname="g_recalc",
        coffee=14000,
        meal=28000,
        rating_avg=4.5,
        rating_count=10,
        match_count=14,
        is_newbie=False,
    )

    create = await client.post(
        "/api/v1/matches",
        headers={"X-User-Id": str(taker.id)},
        json={
            "target_type": "giver",
            "target_id": str(giver_user.id),
            "format": "coffeechat",
            "message": "test",
        },
    )
    match_id = create.json()["id"]
    await client.patch(
        f"/api/v1/matches/{match_id}/accept",
        headers={"X-User-Id": str(giver_user.id)},
    )
    await client.post(
        f"/api/v1/matches/{match_id}/pay",
        headers={"X-User-Id": str(taker.id)},
    )

    await db.refresh(profile)
    assert profile.match_count == 15
    assert profile.is_newbie is False
