from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dev import get_current_user
from app.db.session import get_db
from app.models.db import User
from app.models.schemas.match import (
    MatchCreate,
    MatchResponse,
    MyMatchKind,
    RejectRequest,
)
from app.services import match_service
from app.services.match_service import (
    DuplicateMatch,
    MatchInvalidState,
    MatchNotFound,
    MatchPermissionDenied,
    TargetNotFound,
)

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_match(
    data: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    try:
        match = await match_service.create_match(
            current_user=current_user, data=data, db=db
        )
    except TargetNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        ) from exc
    except DuplicateMatch as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending match already exists between these users",
        ) from exc
    return MatchResponse.model_validate(match)


@router.get("/me", response_model=list[MatchResponse])
async def list_my_matches(
    type: MyMatchKind | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MatchResponse]:
    matches = await match_service.get_my_matches(
        current_user=current_user, kind=type, db=db
    )
    return [MatchResponse.model_validate(m) for m in matches]


def _map_state_exc(exc: Exception) -> HTTPException:
    if isinstance(exc, MatchNotFound):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    if isinstance(exc, MatchInvalidState):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid match state"
        )
    if isinstance(exc, MatchPermissionDenied):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed"
        )
    return HTTPException(status_code=500, detail="Unknown error")


@router.patch("/{match_id}/accept", response_model=MatchResponse)
async def accept_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    try:
        match = await match_service.accept_match(
            match_id=match_id, current_user=current_user, db=db
        )
    except (MatchNotFound, MatchInvalidState, MatchPermissionDenied) as exc:
        raise _map_state_exc(exc) from exc
    return MatchResponse.model_validate(match)


@router.patch("/{match_id}/reject", response_model=MatchResponse)
async def reject_match(
    match_id: uuid.UUID,
    data: RejectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    try:
        match = await match_service.reject_match(
            match_id=match_id,
            current_user=current_user,
            reason=data.reason,
            db=db,
        )
    except (MatchNotFound, MatchInvalidState, MatchPermissionDenied) as exc:
        raise _map_state_exc(exc) from exc
    return MatchResponse.model_validate(match)


@router.post("/{match_id}/pay", response_model=MatchResponse)
async def pay_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    try:
        match = await match_service.pay_match(
            match_id=match_id, current_user=current_user, db=db
        )
    except (MatchNotFound, MatchInvalidState, MatchPermissionDenied) as exc:
        raise _map_state_exc(exc) from exc
    return MatchResponse.model_validate(match)
