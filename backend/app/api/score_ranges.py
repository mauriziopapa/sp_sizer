from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.score_range import ScoreRange
from app.models.user import User
from app.schemas.score_range import ScoreRangeCreate, ScoreRangeUpdate, ScoreRangeResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/score-ranges", tags=["score-ranges"])


@router.get("", response_model=list[ScoreRangeResponse])
async def list_score_ranges(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScoreRange)
        .where(ScoreRange.is_active == True)
        .order_by(ScoreRange.display_order)
    )
    return result.scalars().all()


@router.post("", response_model=ScoreRangeResponse, status_code=status.HTTP_201_CREATED)
async def create_score_range(
    data: ScoreRangeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    sr = ScoreRange(**data.model_dump())
    db.add(sr)
    await db.commit()
    await db.refresh(sr)
    return sr


@router.put("/{range_id}", response_model=ScoreRangeResponse)
async def update_score_range(
    range_id: int,
    data: ScoreRangeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(ScoreRange).where(ScoreRange.id == range_id))
    sr = result.scalar_one_or_none()
    if not sr:
        raise HTTPException(status_code=404, detail="Score range non trovato")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sr, key, value)
    await db.commit()
    await db.refresh(sr)
    return sr
