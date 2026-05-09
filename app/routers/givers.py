from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dev import get_current_user
from app.db.session import get_db
from app.models.db import User
from app.models.schemas.giver import (
    GiverExperienceCreate,
    GiverExperienceResponse,
    GiverProfileCreate,
    GiverProfileResponse,
    GiverProfileUpdate,
)
from app.services import giver_service
from app.services.giver_service import (
    ExperienceAlreadyExists,
    ProfileAlreadyExists,
    ProfileNotFound,
)

router = APIRouter(prefix="/givers", tags=["givers"])


@router.post(
    "/profile",
    response_model=GiverProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_giver_profile(
    data: GiverProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GiverProfileResponse:
    try:
        profile = await giver_service.create_profile(
            user_id=current_user.id, data=data, db=db
        )
    except ProfileAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Giver profile already exists for this user",
        ) from exc
    return GiverProfileResponse.model_validate(profile)


@router.get("/{user_id}", response_model=GiverProfileResponse)
async def get_giver_profile(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GiverProfileResponse:
    """공개 엔드포인트 — 인증 불필요."""
    profile = await giver_service.get_profile_by_user_id(user_id, db)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found",
        )
    return GiverProfileResponse.model_validate(profile)


@router.patch("/profile", response_model=GiverProfileResponse)
async def update_my_giver_profile(
    data: GiverProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GiverProfileResponse:
    try:
        profile = await giver_service.update_profile(
            user_id=current_user.id, data=data, db=db
        )
    except ProfileNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giver profile not found",
        ) from exc
    return GiverProfileResponse.model_validate(profile)


@router.post(
    "/experiences",
    response_model=GiverExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_my_experience(
    data: GiverExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GiverExperienceResponse:
    try:
        experience = await giver_service.add_experience(
            user_id=current_user.id, data=data, db=db
        )
    except ProfileNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your giver profile first",
        ) from exc
    except ExperienceAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Experience already exists (MVP: only one allowed)",
        ) from exc
    return GiverExperienceResponse.model_validate(experience)
