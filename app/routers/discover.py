from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.schemas.discover import (
    DiscoverGiversResponse,
    DiscoverPostsResponse,
    GiverCardResponse,
    PopularTagItem,
    PopularTagsResponse,
    PostCardResponse,
)
from app.services import discover_service

router = APIRouter(prefix="/discover", tags=["discover"])


@router.get("/givers", response_model=DiscoverGiversResponse)
async def list_givers(
    q: str | None = Query(None),
    categories: list[str] | None = Query(None),
    format: list[str] | None = Query(None),
    price_min: int = Query(0, ge=0),
    price_max: int = Query(99999999, ge=0),
    rating_min: float = Query(0.0, ge=0.0, le=5.0),
    tag: str | None = Query(None),
    sort: str = Query("latest"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> DiscoverGiversResponse:
    total, items = await discover_service.search_givers(
        q=q,
        categories=categories,
        formats=format,
        price_min=price_min,
        price_max=price_max,
        rating_min=rating_min,
        tag=tag,
        sort=sort,
        page=page,
        size=size,
        db=db,
    )
    return DiscoverGiversResponse(
        total=total,
        page=page,
        items=[GiverCardResponse(**item) for item in items],
    )


@router.get("/posts", response_model=DiscoverPostsResponse)
async def list_posts(
    q: str | None = Query(None),
    categories: list[str] | None = Query(None),
    format: list[str] | None = Query(None),
    budget_min: int | None = Query(None, ge=0),
    budget_max: int | None = Query(None, ge=0),
    active_only: bool = Query(False),
    tag: str | None = Query(None),
    sort: str = Query("latest"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> DiscoverPostsResponse:
    total, items = await discover_service.search_posts(
        q=q,
        categories=categories,
        formats=format,
        budget_min=budget_min,
        budget_max=budget_max,
        active_only=active_only,
        tag=tag,
        sort=sort,
        page=page,
        size=size,
        db=db,
    )
    return DiscoverPostsResponse(
        total=total,
        page=page,
        items=[PostCardResponse(**item) for item in items],
    )


@router.get("/popular-tags", response_model=PopularTagsResponse)
async def list_popular_tags(
    db: AsyncSession = Depends(get_db),
) -> PopularTagsResponse:
    rows = await discover_service.get_popular_tags(db, limit=10)
    return PopularTagsResponse(tags=[PopularTagItem(**r) for r in rows])
