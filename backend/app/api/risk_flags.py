from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.risk_flag import RiskFlag
from app.models.user import User
from app.schemas.risk_flag import RiskFlagCreate, RiskFlagUpdate, RiskFlagResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/risk-flags", tags=["risk-flags"])


@router.get("", response_model=list[RiskFlagResponse])
async def list_risk_flags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RiskFlag)
        .where(RiskFlag.is_active == True)
        .order_by(RiskFlag.display_order)
    )
    return result.scalars().all()


@router.post("", response_model=RiskFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_flag(
    data: RiskFlagCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    flag = RiskFlag(**data.model_dump())
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return flag


@router.put("/{flag_id}", response_model=RiskFlagResponse)
async def update_risk_flag(
    flag_id: int,
    data: RiskFlagUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(RiskFlag).where(RiskFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Risk flag non trovato")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(flag, key, value)
    await db.commit()
    await db.refresh(flag)
    return flag
