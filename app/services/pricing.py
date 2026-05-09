"""Giver 가격 자동 산정 — PRD §8.2 의사코드의 직접 구현.

순수 함수: DB/외부 의존 없음.
"""

from __future__ import annotations

from decimal import Decimal

COFFEE_MIN, COFFEE_MAX = 5000, 25000
MEAL_MIN, MEAL_MAX = 10000, 50000

NEWBIE_MATCH_THRESHOLD = 3
ACTIVITY_DENOMINATOR = 27  # 30건 도달 시 만점 (=30 - NEWBIE_MATCH_THRESHOLD)
RATING_FLOOR = 3.0
RATING_CEIL = 5.0
ROUND_UNIT = 500

RATING_WEIGHT = 0.6
ACTIVITY_WEIGHT = 0.4


def calculate_pricing_score(match_count: int, rating_avg: float) -> float:
    """0.0 ~ 1.0 점수. PRD §8.2.

    신규(<3건)는 점수가 의미 없으므로 0.0 반환 (산정에서 분기됨).
    """
    if match_count < NEWBIE_MATCH_THRESHOLD:
        return 0.0
    rating_norm = max(0.0, (rating_avg - RATING_FLOOR) / (RATING_CEIL - RATING_FLOOR))
    activity_norm = min(
        1.0, (match_count - NEWBIE_MATCH_THRESHOLD) / ACTIVITY_DENOMINATOR
    )
    return RATING_WEIGHT * rating_norm + ACTIVITY_WEIGHT * activity_norm


def _interpolate(low: int, high: int, score: float) -> int:
    raw = int(low + (high - low) * score)
    return round(raw / ROUND_UNIT) * ROUND_UNIT


def recalculate_giver_pricing(
    match_count: int, rating_avg: float | Decimal
) -> tuple[int, int]:
    """평점·활동 빈도 기반 (커피챗, 밀챗) 가격 산정.

    PRD §8.2 의사코드 정확 구현. match_count<3 시 하한선 고정.
    """
    rating_avg_f = float(rating_avg)

    if match_count < NEWBIE_MATCH_THRESHOLD:
        return COFFEE_MIN, MEAL_MIN

    score = calculate_pricing_score(match_count, rating_avg_f)
    coffee = _interpolate(COFFEE_MIN, COFFEE_MAX, score)
    meal = _interpolate(MEAL_MIN, MEAL_MAX, score)
    return coffee, meal
