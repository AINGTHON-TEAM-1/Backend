"""PRD §8.2 가격 산정 의사코드의 정확 계산값을 검증.

표(예시)와 의사코드 실제 계산이 B의 mealchat, D의 coffeechat에서 500원씩 차이 — 의사코드를 진실의 원천으로 채택.
"""

from __future__ import annotations

import pytest

from app.services.pricing import (
    COFFEE_MAX,
    COFFEE_MIN,
    MEAL_MAX,
    MEAL_MIN,
    recalculate_giver_pricing,
)


@pytest.mark.parametrize(
    ("match_count", "rating_avg", "expected"),
    [
        # PRD §8.2 시나리오 5종 (의사코드 정확 계산값)
        pytest.param(0, 0.0, (5000, 10000), id="A_newbie"),
        pytest.param(5, 4.0, (11500, 23000), id="B_rookie"),
        pytest.param(15, 4.5, (17500, 35000), id="C_active"),
        pytest.param(30, 4.8, (24000, 47500), id="D_popular"),
        pytest.param(20, 3.2, (11000, 22500), id="E_low_rating"),
    ],
)
def test_recalculate_giver_pricing_prd_scenarios(
    match_count: int, rating_avg: float, expected: tuple[int, int]
) -> None:
    assert recalculate_giver_pricing(match_count, rating_avg) == expected


def test_below_newbie_threshold_returns_floor() -> None:
    """match_count<3은 평점과 무관하게 하한선."""
    for mc in (0, 1, 2):
        assert recalculate_giver_pricing(mc, 5.0) == (COFFEE_MIN, MEAL_MIN)


def test_max_score_returns_ceiling() -> None:
    """평점 5.0 + 매칭 30건 이상 → 만점 → 상한선."""
    assert recalculate_giver_pricing(30, 5.0) == (COFFEE_MAX, MEAL_MAX)
    assert recalculate_giver_pricing(100, 5.0) == (COFFEE_MAX, MEAL_MAX)


def test_low_rating_clamped_to_zero() -> None:
    """평점 3.0 이하는 정규화 0으로 clamp — 활동 빈도만 반영."""
    # rating=2.0 (음수가 되어야 하지만 max(0, ...) 처리), match=30 → activity_norm=1.0
    # score = 0.6*0 + 0.4*1.0 = 0.4
    coffee, meal = recalculate_giver_pricing(30, 2.0)
    assert coffee == 13000  # 5000 + 20000*0.4 = 13000
    assert meal == 26000  # 10000 + 40000*0.4 = 26000


def test_threshold_boundary_three_matches() -> None:
    """match=3은 신규 졸업 (<3 아님). score=0이라 하한선과 동일."""
    # rating=3.0 → rating_norm=0, activity=(3-3)/27=0 → score=0
    assert recalculate_giver_pricing(3, 3.0) == (COFFEE_MIN, MEAL_MIN)
